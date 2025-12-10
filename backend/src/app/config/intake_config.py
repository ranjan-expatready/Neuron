from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

import yaml


@dataclass
class FieldDefinition:
    id: str
    label: str
    data_path: str
    type: str
    ui_control: Optional[str] = None
    options_ref: Optional[Any] = None
    validations: dict[str, Any] = field(default_factory=dict)
    visibility_conditions: Optional[Any] = None
    group: Optional[str] = None
    help_text: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    required: Optional[bool] = None


@dataclass
class IntakeStep:
    id: str
    label: str
    fields: List[str] = field(default_factory=list)


@dataclass
class IntakeTemplate:
    id: str
    label: str
    applicable_programs: List[str] = field(default_factory=list)
    applicable_plans: List[str] = field(default_factory=list)
    steps: List[IntakeStep] = field(default_factory=list)


@dataclass
class DocumentDefinition:
    id: str
    label: str
    category: str
    required_for_programs: List[str] = field(default_factory=list)
    required_when: List[dict[str, Any]] = field(default_factory=list)


@dataclass
class FormDefinition:
    id: str
    label: str
    applicable_programs: List[str] = field(default_factory=list)
    field_mappings: dict[str, str] = field(default_factory=dict)


@dataclass
class IntakeConfigBundle:
    fields: List[FieldDefinition] = field(default_factory=list)
    templates: List[IntakeTemplate] = field(default_factory=list)
    documents: List[DocumentDefinition] = field(default_factory=list)
    forms: List[FormDefinition] = field(default_factory=list)


class IntakeConfigLoader:
    """
    Minimal, read-only loader for intake/document/form configs.
    Does basic shape validation and keeps runtime logic untouched (M6.1 scaffold only).
    """

    def __init__(self, base_path: Optional[Path] = None) -> None:
        # repo root = parents[4] (backend/src/app/config/*)
        self.base_path = base_path or Path(__file__).resolve().parents[4] / "config" / "domain"

    def _load_yaml(self, name: str) -> dict[str, Any]:
        path = self.base_path / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Missing config file: {path}")
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def load(self) -> IntakeConfigBundle:
        fields_raw = self._load_yaml("fields").get("fields", [])
        templates_raw = self._load_yaml("intake_templates").get("intake_templates", [])
        documents_raw = self._load_yaml("documents").get("document_definitions", [])
        forms_raw = self._load_yaml("forms").get("form_definitions", [])

        fields = [FieldDefinition(**item) for item in fields_raw if isinstance(item, dict) and "id" in item]
        templates: List[IntakeTemplate] = []
        for tpl in templates_raw:
            if not isinstance(tpl, dict) or "id" not in tpl:
                continue
            steps = [IntakeStep(**step) for step in tpl.get("steps", []) if isinstance(step, dict) and "id" in step]
            templates.append(
                IntakeTemplate(
                    id=tpl["id"],
                    label=tpl.get("label", tpl["id"]),
                    applicable_programs=tpl.get("applicable_programs", []),
                    applicable_plans=tpl.get("applicable_plans", []),
                    steps=steps,
                )
            )

        documents = [
            DocumentDefinition(**doc) for doc in documents_raw if isinstance(doc, dict) and "id" in doc
        ]
        forms = [FormDefinition(**frm) for frm in forms_raw if isinstance(frm, dict) and "id" in frm]

        return IntakeConfigBundle(fields=fields, templates=templates, documents=documents, forms=forms)


