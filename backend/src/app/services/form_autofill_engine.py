from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from src.app.cases.repository import CaseRepository
from src.app.config.form_config import (
    FormConfigError,
    FormFieldMapping,
    FormDefinition,
    FormBundleDefinition,
    load_form_bundles,
    load_form_definitions,
    load_form_mappings,
)
from src.app.domain.forms.models import FormAutofillPreviewResult, FormAutofillResult, FormFieldAutofill
from src.app.models.document import Document
from src.app.services.profile_mapping import get_by_path


class FormAutofillEngineError(Exception):
    """Base error for form autofill engine."""


class FormAutofillEngine:
    """
    Backend-only service that resolves form field values from canonical profile and config mappings.
    No DB mutations, no PDF/web automation, no public API wiring (M10.3 foundation).
    """

    def __init__(self, base_path: Optional[str] = None):
        self._base_path = base_path

    def _load_forms(self) -> List[FormDefinition]:
        return load_form_definitions(base_path=self._base_path)

    def _load_mappings(self) -> List[FormFieldMapping]:
        return load_form_mappings(base_path=self._base_path)

    def _load_bundles(self) -> List[FormBundleDefinition]:
        return load_form_bundles(base_path=self._base_path)

    def _get_case_profile(self, db_session: Session, case_id: str, tenant_id: str) -> Dict[str, Any]:
        repo = CaseRepository(db_session)
        record = repo.get_case(case_id, tenant_id=tenant_id)
        if not record:
            raise FormAutofillEngineError("Case not found or tenant mismatch")
        profile = record.profile or {}
        if "profile" not in profile:
            profile = {"profile": profile}
        return profile

    def _get_case_documents(self, db_session: Session, case_id: str, tenant_id: str) -> List[Document]:
        return (
            db_session.query(Document)
            .filter(Document.case_id == case_id, Document.org_id == tenant_id)
            .all()
        )

    def _pick_bundle(self, bundles: List[FormBundleDefinition], program_code: Optional[str]) -> Optional[FormBundleDefinition]:
        if program_code:
            for bundle in bundles:
                if program_code in bundle.program_codes:
                    return bundle
        return bundles[0] if bundles else None

    def _resolve_mapping_value(
        self,
        mapping: FormFieldMapping,
        profile: Dict[str, Any],
        documents: List[Document],
    ) -> FormFieldAutofill:
        notes: List[str] = []
        value: Any = None
        source_path: Optional[str] = mapping.source_path

        if mapping.source_type == "canonical_profile":
            value = get_by_path(profile, source_path or "")
            if value is None:
                notes.append("missing canonical data")
        elif mapping.source_type == "document":
            # Interpret source_path as document_type identifier
            doc = next((d for d in documents if d.document_type == source_path), None)
            if doc:
                value = {"document_id": doc.id, "filename": doc.filename, "document_type": doc.document_type}
            else:
                notes.append("document not found")
        elif mapping.source_type == "constant":
            value = mapping.source_path
        elif mapping.source_type == "rule_engine":
            notes.append("rule_engine source not implemented in M10.3")
        else:
            raise FormAutofillEngineError(f"Unsupported source_type: {mapping.source_type}")

        return FormFieldAutofill(
            form_id=mapping.form_id,
            field_id=mapping.field_id,
            proposed_value=value,
            source_type=mapping.source_type,  # type: ignore[arg-type]
            source_path=source_path,
            notes="; ".join(notes) if notes else None,
            conflicts=[],
        )

    def build_autofill_preview(
        self,
        *,
        case_id: str,
        program_code: Optional[str],
        tenant_id: str,
        db_session: Session,
    ) -> FormAutofillPreviewResult:
        preview_warnings: List[str] = []
        try:
            forms = self._load_forms()
            mappings = self._load_mappings()
            try:
                bundles = self._load_bundles()
            except FormConfigError as exc:
                preview_warnings.append(str(exc))
                bundles = []
        except FormConfigError as exc:
            raise FormAutofillEngineError(str(exc)) from exc

        profile = self._get_case_profile(db_session, case_id, tenant_id)
        documents = self._get_case_documents(db_session, case_id, tenant_id)

        bundle = self._pick_bundle(bundles, program_code)
        target_form_ids = set(bundle.forms) if bundle else {f.id for f in forms}

        forms_by_id = {f.id: f for f in forms}
        mappings_by_form: Dict[str, List[FormFieldMapping]] = {}
        for m in mappings:
            mappings_by_form.setdefault(m.form_id, []).append(m)

        preview_forms: List[FormAutofillResult] = []
        for form_id in target_form_ids:
            definition = forms_by_id.get(form_id)
            if not definition:
                preview_warnings.append(f"Form {form_id} referenced in bundle but not defined")
                continue

            form_mappings = mappings_by_form.get(form_id, [])
            form_fields: List[FormFieldAutofill] = []
            if not form_mappings:
                preview_warnings.append(f"No mappings found for form {form_id}")
            else:
                for mapping in form_mappings:
                    try:
                        form_fields.append(self._resolve_mapping_value(mapping, profile, documents))
                    except FormAutofillEngineError as exc:
                        preview_warnings.append(f"{form_id}:{mapping.field_id} error: {exc}")

            preview_forms.append(
                FormAutofillResult(
                    form_id=form_id,
                    fields=form_fields,
                    warnings=[],
                )
            )

        return FormAutofillPreviewResult(
            bundle_id=bundle.id if bundle else None,
            forms=preview_forms,
            warnings=preview_warnings,
        )

