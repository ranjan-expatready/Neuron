from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field, ValidationError, root_validator, validator


class IntakeConfigError(Exception):
    """Base exception for intake config issues."""


class MissingReferenceError(IntakeConfigError):
    """Raised when cross-file references are invalid."""


class DocumentCondition(BaseModel):
    field: str
    equals: Optional[Any] = None
    not_equals: Optional[Any] = None
    greater_than: Optional[Union[int, float]] = None
    greater_or_equal: Optional[Union[int, float]] = None
    in_set: Optional[List[Any]] = Field(default=None, alias="in")
    not_in_set: Optional[List[Any]] = Field(default=None, alias="not_in")

    @root_validator(skip_on_failure=True)
    def ensure_operator_present(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not any(
            values.get(key)
            for key in (
                "equals",
                "not_equals",
                "greater_than",
                "greater_or_equal",
                "in_set",
                "not_in_set",
            )
        ):
            raise ValueError("DocumentCondition requires at least one operator")
        return values


class FieldDefinition(BaseModel):
    id: str
    label: str
    data_path: str
    type: str
    ui_control: Optional[str] = None
    options_ref: Optional[Any] = None
    validations: Dict[str, Any] = Field(default_factory=dict)
    visibility_conditions: Optional[Any] = None
    group: Optional[str] = None
    help_text: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    required: Optional[bool] = None


class IntakeStep(BaseModel):
    id: str
    label: str
    fields: List[str] = Field(default_factory=list)


class IntakeTemplate(BaseModel):
    id: str
    label: str
    applicable_programs: List[str] = Field(default_factory=list)
    applicable_plans: List[str] = Field(default_factory=list)
    steps: List[IntakeStep] = Field(default_factory=list)


class DocumentDefinition(BaseModel):
    id: str
    label: str
    category: str
    required_for_programs: List[str] = Field(default_factory=list)
    required_when: List[DocumentCondition] = Field(default_factory=list)


class FormDefinition(BaseModel):
    id: str
    label: str
    applicable_programs: List[str] = Field(default_factory=list)
    field_mappings: Dict[str, str] = Field(default_factory=dict)

    @validator("field_mappings")
    def validate_field_mappings(cls, value: Dict[str, str]) -> Dict[str, str]:
        for k, v in value.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise ValueError("form field mappings must map strings to strings")
        return value


class IntakeConfigBundle(BaseModel):
    fields: List[FieldDefinition] = Field(default_factory=list)
    templates: List[IntakeTemplate] = Field(default_factory=list)
    documents: List[DocumentDefinition] = Field(default_factory=list)
    forms: List[FormDefinition] = Field(default_factory=list)


def _default_base_path() -> Path:
    return Path(__file__).resolve().parents[4] / "config" / "domain"


def _load_yaml(base_path: Path, name: str) -> dict[str, Any]:
    path = base_path / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _base_path_key(base_path: Optional[Path]) -> str:
    return str(base_path or _default_base_path())


@lru_cache(maxsize=8)
def load_fields_config(base_path: Optional[str] = None) -> List[FieldDefinition]:
    base = Path(base_path) if base_path else _default_base_path()
    raw = _load_yaml(base, "fields").get("fields", [])
    try:
        return [FieldDefinition(**item) for item in raw if isinstance(item, dict)]
    except ValidationError as err:
        raise IntakeConfigError(f"Invalid fields.yaml: {err}") from err


@lru_cache(maxsize=8)
def load_intake_templates_config(base_path: Optional[str] = None) -> List[IntakeTemplate]:
    base = Path(base_path) if base_path else _default_base_path()
    raw = _load_yaml(base, "intake_templates").get("intake_templates", [])
    try:
        return [IntakeTemplate(**item) for item in raw if isinstance(item, dict)]
    except ValidationError as err:
        raise IntakeConfigError(f"Invalid intake_templates.yaml: {err}") from err


@lru_cache(maxsize=8)
def load_documents_config(base_path: Optional[str] = None) -> List[DocumentDefinition]:
    base = Path(base_path) if base_path else _default_base_path()
    raw = _load_yaml(base, "documents").get("document_definitions", [])
    try:
        return [DocumentDefinition(**item) for item in raw if isinstance(item, dict)]
    except ValidationError as err:
        raise IntakeConfigError(f"Invalid documents.yaml: {err}") from err


@lru_cache(maxsize=8)
def load_forms_config(base_path: Optional[str] = None) -> List[FormDefinition]:
    base = Path(base_path) if base_path else _default_base_path()
    raw = _load_yaml(base, "forms").get("form_definitions", [])
    try:
        return [FormDefinition(**item) for item in raw if isinstance(item, dict)]
    except ValidationError as err:
        raise IntakeConfigError(f"Invalid forms.yaml: {err}") from err


def _validate_cross_references(
    fields: List[FieldDefinition],
    templates: List[IntakeTemplate],
    documents: List[DocumentDefinition],
    forms: List[FormDefinition],
) -> None:
    field_ids = {f.id for f in fields}
    data_paths = {f.data_path for f in fields}
    valid_targets = field_ids.union(data_paths)

    def _is_known_target(target: str) -> bool:
        # Allow explicit field ids, known data paths, or free-form canonical paths.
        return target in valid_targets or "." in target

    for tpl in templates:
        for step in tpl.steps:
            for fid in step.fields:
                if fid not in field_ids:
                    raise MissingReferenceError(f"Template {tpl.id} references unknown field '{fid}'")

    for doc in documents:
        for cond in doc.required_when:
            if not _is_known_target(cond.field):
                raise MissingReferenceError(
                    f"Document {doc.id} condition references unknown field '{cond.field}'"
                )

    for form in forms:
        for mapping in form.field_mappings.values():
            if not _is_known_target(mapping):
                raise MissingReferenceError(
                    f"Form {form.id} mapping references unknown field or path '{mapping}'"
                )


def load_intake_bundle(base_path: Optional[Path] = None) -> IntakeConfigBundle:
    base_key = _base_path_key(base_path)
    fields = load_fields_config(base_key)
    templates = load_intake_templates_config(base_key)
    documents = load_documents_config(base_key)
    forms = load_forms_config(base_key)
    _validate_cross_references(fields, templates, documents, forms)
    return IntakeConfigBundle(fields=fields, templates=templates, documents=documents, forms=forms)


def clear_intake_config_cache() -> None:
    """Helper to clear all caches (used in tests)."""
    load_fields_config.cache_clear()
    load_intake_templates_config.cache_clear()
    load_documents_config.cache_clear()
    load_forms_config.cache_clear()
