from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError, validator


class FormConfigError(Exception):
    """Base exception for form config issues."""


class MissingReferenceError(FormConfigError):
    """Raised when cross-file references are invalid."""


class FormFieldDefinition(BaseModel):
    field_id: str
    label: str
    data_type: str
    required: bool = False
    allowed_values: Optional[List[Any]] = None
    description: Optional[str] = None
    hints: Optional[str] = None
    section: Optional[str] = None


class FormSection(BaseModel):
    id: str
    label: str


class FormDefinition(BaseModel):
    id: str
    label: str
    version: str
    status: str = Field(..., pattern="^(draft|active|retired)$")
    type: str = Field(..., pattern="^(pdf|web)$")
    applicable_programs: List[str] = Field(default_factory=list)
    sections: List[FormSection] = Field(default_factory=list)
    fields: List[FormFieldDefinition] = Field(default_factory=list)
    field_mappings: Dict[str, str] = Field(default_factory=dict)


class FormFieldMapping(BaseModel):
    id: str
    form_id: str
    field_id: str
    source_type: str = Field(..., pattern="^(canonical_profile|document|rule_engine|constant)$")
    source_path: str
    transform: Optional[str] = None
    status: str = Field(..., pattern="^(draft|active|retired)$")
    notes: Optional[str] = None


class FormBundleDefinition(BaseModel):
    id: str
    label: str
    program_codes: List[str] = Field(default_factory=list)
    forms: List[str] = Field(default_factory=list)
    status: str = Field(..., pattern="^(draft|active|retired)$")

    @validator("forms")
    def ensure_forms(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("form bundle must include at least one form id")
        return value


def _default_base_path() -> Path:
    return Path(__file__).resolve().parents[4] / "config" / "domain"


def _load_yaml(base_path: Path, name: str) -> dict[str, Any]:
    path = base_path / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _base_key(base_path: Optional[str | Path]) -> str:
    return str(base_path or _default_base_path())


@lru_cache(maxsize=8)
def _load_forms_cached(base_key: str) -> List[FormDefinition]:
    base = Path(base_key)
    raw = _load_yaml(base, "forms").get("form_definitions", [])
    try:
        return [FormDefinition(**item) for item in raw if isinstance(item, dict)]
    except ValidationError as err:
        raise FormConfigError(f"Invalid forms.yaml: {err}") from err


@lru_cache(maxsize=8)
def _load_mappings_cached(base_key: str) -> List[FormFieldMapping]:
    base = Path(base_key)
    raw = _load_yaml(base, "form_mappings").get("form_field_mappings", [])
    try:
        return [FormFieldMapping(**item) for item in raw if isinstance(item, dict)]
    except ValidationError as err:
        raise FormConfigError(f"Invalid form_mappings.yaml: {err}") from err


@lru_cache(maxsize=8)
def _load_bundles_cached(base_key: str) -> List[FormBundleDefinition]:
    base = Path(base_key)
    raw = _load_yaml(base, "form_bundles").get("form_bundles", [])
    try:
        return [FormBundleDefinition(**item) for item in raw if isinstance(item, dict)]
    except ValidationError as err:
        raise FormConfigError(f"Invalid form_bundles.yaml: {err}") from err


def load_form_definitions(base_path: Optional[str | Path] = None) -> List[FormDefinition]:
    return _load_forms_cached(_base_key(base_path))


def load_form_mappings(base_path: Optional[str | Path] = None) -> List[FormFieldMapping]:
    base = _base_key(base_path)
    forms = {f.id: f for f in _load_forms_cached(base)}
    mappings = _load_mappings_cached(base)

    for mapping in mappings:
        if mapping.form_id not in forms:
            raise MissingReferenceError(f"Mapping {mapping.id} references unknown form_id={mapping.form_id}")
        form = forms[mapping.form_id]
        if not any(field.field_id == mapping.field_id for field in form.fields):
            raise MissingReferenceError(
                f"Mapping {mapping.id} references unknown field_id={mapping.field_id} for form_id={mapping.form_id}"
            )
    return mappings


def load_form_bundles(base_path: Optional[str | Path] = None) -> List[FormBundleDefinition]:
    base = _base_key(base_path)
    forms = {f.id: f for f in _load_forms_cached(base)}
    bundles = _load_bundles_cached(base)

    for bundle in bundles:
        missing = [fid for fid in bundle.forms if fid not in forms]
        if missing:
            raise MissingReferenceError(
                f"Bundle {bundle.id} references unknown form ids: {', '.join(sorted(missing))}"
            )
    return bundles


def clear_caches() -> None:
    _load_forms_cached.cache_clear()
    _load_mappings_cached.cache_clear()
    _load_bundles_cached.cache_clear()

