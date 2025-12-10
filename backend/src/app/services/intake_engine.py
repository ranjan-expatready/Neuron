from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.app.cases.models_db import CaseRecord
from src.app.config.intake_config import (
    DocumentCondition,
    DocumentDefinition,
    FieldDefinition,
    IntakeConfigBundle,
    IntakeTemplate,
    clear_intake_config_cache,
    load_intake_bundle,
)


def _get_value(profile: Dict[str, Any], path: str) -> Any:
    """
    Traverse a nested dict using a dotted path.
    Supports paths that optionally start with 'profile.'.
    """
    current = profile
    parts = path.split(".")
    if parts and parts[0] == "profile":
        if "profile" in profile and isinstance(profile.get("profile"), dict):
            current = profile.get("profile", {})
        parts = parts[1:]
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current.get(part)
    return current


def _matches_program(programs: List[str], program_code: str) -> bool:
    return any(p.lower() == program_code.lower() for p in programs)


def _evaluate_condition(
    cond: DocumentCondition,
    profile: Dict[str, Any],
    field_lookup: Dict[str, FieldDefinition],
) -> tuple[bool, Optional[str]]:
    target_path = field_lookup.get(cond.field).data_path if cond.field in field_lookup else cond.field
    value = _get_value(profile, target_path)

    if cond.equals is not None:
        result = value == cond.equals
        return result, f"{cond.field} == {cond.equals}"
    if cond.not_equals is not None:
        result = value != cond.not_equals
        return result, f"{cond.field} != {cond.not_equals}"
    if cond.greater_than is not None:
        try:
            result = value is not None and float(value) > float(cond.greater_than)
        except (TypeError, ValueError):
            result = False
        return result, f"{cond.field} > {cond.greater_than}"
    if cond.greater_or_equal is not None:
        try:
            result = value is not None and float(value) >= float(cond.greater_or_equal)
        except (TypeError, ValueError):
            result = False
        return result, f"{cond.field} >= {cond.greater_or_equal}"
    if cond.in_set is not None:
        result = value in cond.in_set
        return result, f"{cond.field} in {cond.in_set}"
    if cond.not_in_set is not None:
        result = value not in cond.not_in_set
        return result, f"{cond.field} not in {cond.not_in_set}"
    return False, None


@dataclass
class ResolvedField:
    id: str
    label: str
    data_path: str
    type: str
    ui_control: Optional[str]
    options_ref: Optional[Any]
    validations: Dict[str, Any]
    visibility_conditions: Optional[Any]
    group: Optional[str]
    help_text: Optional[str]
    tags: List[str]
    required: Optional[bool]

    @classmethod
    def from_definition(cls, field: FieldDefinition) -> "ResolvedField":
        return cls(
            id=field.id,
            label=field.label,
            data_path=field.data_path,
            type=field.type,
            ui_control=field.ui_control,
            options_ref=field.options_ref,
            validations=field.validations,
            visibility_conditions=field.visibility_conditions,
            group=field.group,
            help_text=field.help_text,
            tags=field.tags,
            required=field.required,
        )


@dataclass
class IntakeStepResolved:
    id: str
    label: str
    fields: List[ResolvedField]


@dataclass
class IntakeTemplateResolved:
    id: str
    label: str
    applicable_programs: List[str]
    applicable_plans: List[str]
    steps: List[IntakeStepResolved]


@dataclass
class DocumentRequirementResolved:
    id: str
    label: str
    category: str
    required: bool
    reasons: List[str]


class IntakeEngine:
    """
    Provides resolved intake schema and document checklist based on config files.
    """

    def __init__(self, base_path: Optional[Path] = None) -> None:
        self.base_path = base_path

    def _bundle(self) -> IntakeConfigBundle:
        return load_intake_bundle(self.base_path)

    def _field_lookup(self) -> Dict[str, FieldDefinition]:
        return {f.id: f for f in self._bundle().fields}

    def get_intake_schema_for_program(
        self, program_code: str, plan_code: Optional[str] = None
    ) -> IntakeTemplateResolved:
        bundle = self._bundle()
        plan_code_lower = plan_code.lower() if plan_code else None

        def _plan_matches(template: IntakeTemplate) -> bool:
            if not template.applicable_plans:
                return True
            if plan_code_lower is None:
                return True
            return any(plan.lower() == plan_code_lower for plan in template.applicable_plans)

        candidates = [
            tpl
            for tpl in bundle.templates
            if _matches_program(tpl.applicable_programs, program_code) and _plan_matches(tpl)
        ]
        if not candidates:
            raise ValueError(f"No intake template found for program {program_code}")

        field_lookup = self._field_lookup()
        template = candidates[0]
        resolved_steps = []
        for step in template.steps:
            resolved_fields = [ResolvedField.from_definition(field_lookup[fid]) for fid in step.fields]
            resolved_steps.append(
                IntakeStepResolved(
                    id=step.id,
                    label=step.label,
                    fields=resolved_fields,
                )
            )

        return IntakeTemplateResolved(
            id=template.id,
            label=template.label,
            applicable_programs=template.applicable_programs,
            applicable_plans=template.applicable_plans,
            steps=resolved_steps,
        )

    def _is_required_for_program(self, doc: DocumentDefinition, program_code: str) -> bool:
        if not doc.required_for_programs:
            return True
        return _matches_program(doc.required_for_programs, program_code)

    def _evaluate_document(
        self,
        doc: DocumentDefinition,
        profile: Dict[str, Any],
        program_code: str,
        field_lookup: Dict[str, FieldDefinition],
    ) -> DocumentRequirementResolved:
        reasons: List[str] = []
        required = self._is_required_for_program(doc, program_code)
        if not required:
            return DocumentRequirementResolved(
                id=doc.id, label=doc.label, category=doc.category, required=False, reasons=["program_not_applicable"]
            )

        if not doc.required_when:
            reasons.append("program_applicable")
            return DocumentRequirementResolved(
                id=doc.id, label=doc.label, category=doc.category, required=True, reasons=reasons
            )

        for cond in doc.required_when:
            result, reason = _evaluate_condition(cond, profile, field_lookup)
            if not result:
                return DocumentRequirementResolved(
                    id=doc.id,
                    label=doc.label,
                    category=doc.category,
                    required=False,
                    reasons=[reason or "condition_not_met"],
                )
            if reason:
                reasons.append(reason)

        if not reasons:
            reasons.append("conditions_met")
        return DocumentRequirementResolved(
            id=doc.id, label=doc.label, category=doc.category, required=True, reasons=reasons
        )

    def get_document_checklist_for_profile(
        self, profile: Dict[str, Any], program_code: str
    ) -> List[DocumentRequirementResolved]:
        bundle = self._bundle()
        field_lookup = self._field_lookup()
        checklist: List[DocumentRequirementResolved] = []
        for doc in bundle.documents:
            checklist.append(self._evaluate_document(doc, profile, program_code, field_lookup))
        return checklist

    def _infer_program_from_case(self, case: CaseRecord) -> Optional[str]:
        prog = None
        if isinstance(case.program_eligibility, dict):
            results = case.program_eligibility.get("results")
            if isinstance(results, list):
                for item in results:
                    if isinstance(item, dict) and item.get("eligible"):
                        prog = item.get("program_code")
                        if prog:
                            return prog
        return prog

    def get_document_checklist_for_case(
        self, case: CaseRecord, program_code: Optional[str] = None
    ) -> List[DocumentRequirementResolved]:
        resolved_program = program_code or self._infer_program_from_case(case)
        if not resolved_program:
            raise ValueError("Program code is required to resolve document checklist")
        profile_data = case.profile or {}
        return self.get_document_checklist_for_profile(profile_data, resolved_program)


__all__ = [
    "IntakeEngine",
    "IntakeTemplateResolved",
    "IntakeStepResolved",
    "ResolvedField",
    "DocumentRequirementResolved",
    "clear_intake_config_cache",
]

