from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from src.app.cases.repository import CaseRepository
from src.app.config.form_config import (
    FormConfigError,
    FormDefinition,
    load_form_bundles,
    load_form_definitions,
    load_form_mappings,
)
from src.app.domain.forms.models import FormAutofillPreviewResult
from src.app.domain.submission.models import (
    FormReadinessSummary,
    ReadinessCheckResult,
    ReadinessSeverity,
    SubmissionReadinessReport,
)
from src.app.documents.service import DocumentMatrixService
from src.app.domain_config.service import ConfigService
from src.app.models.document import Document
from src.app.rules.models import CandidateProfile
from src.app.services.form_autofill_engine import FormAutofillEngine, FormAutofillEngineError


class SubmissionReadinessError(Exception):
    """Base error for submission readiness."""


class SubmissionReadinessService:
    """
    Deterministic, read-only readiness evaluator for form bundles.
    No DB writes, no LLM/OCR, no external calls.
    """

    def __init__(
        self,
        *,
        base_path: Optional[str | Path] = None,
        config_service: Optional[ConfigService] = None,
        autofill_engine: Optional[FormAutofillEngine] = None,
        document_service: Optional[DocumentMatrixService] = None,
    ) -> None:
        self._base_path = Path(base_path) if base_path else None
        self.config_service = config_service or ConfigService(base_path=self._base_path)
        self.autofill_engine = autofill_engine or FormAutofillEngine(base_path=str(self._base_path) if self._base_path else None)
        self.document_service = document_service or DocumentMatrixService(self.config_service, base_path=self._base_path)

    def _load_forms_bundle(
        self, bundle_id: str
    ) -> Tuple[Dict[str, FormDefinition], List[str], List[str]]:
        try:
            forms = load_form_definitions(base_path=self._base_path)
            mappings = load_form_mappings(base_path=self._base_path)
            bundles = load_form_bundles(base_path=self._base_path)
        except FormConfigError as exc:
            raise SubmissionReadinessError(str(exc)) from exc

        bundle = next((b for b in bundles if b.id == bundle_id), None)
        if not bundle:
            raise SubmissionReadinessError("Invalid bundle_id")

        forms_by_id = {f.id: f for f in forms if f.id in bundle.forms}
        return forms_by_id, list(bundle.forms), list(bundle.program_codes)

    def _convert_profile(self, profile: dict) -> CandidateProfile:
        canonical = profile.get("profile", profile)
        try:
            return CandidateProfile.parse_obj(canonical)
        except Exception as exc:
            raise SubmissionReadinessError(f"Invalid canonical profile: {exc}") from exc

    def _get_case_documents(self, db_session: Session, case_id: str, tenant_id: str) -> List[Document]:
        return (
            db_session.query(Document)
            .filter(Document.case_id == case_id, Document.org_id == tenant_id)
            .all()
        )

    def _evaluate_forms(
        self,
        preview: FormAutofillPreviewResult,
        forms_by_id: Dict[str, FormDefinition],
    ) -> Tuple[List[FormReadinessSummary], int, int, int, List[str]]:
        summaries: List[FormReadinessSummary] = []
        total_required = 0
        total_present = 0
        blockers = 0
        warnings = 0
        notes: List[str] = list(preview.warnings or [])

        preview_by_id = {f.form_id: f for f in preview.forms}

        for form_id, definition in forms_by_id.items():
            preview_form = preview_by_id.get(form_id)
            form_checks: List[ReadinessCheckResult] = []
            required_fields = [fld for fld in definition.fields if getattr(fld, "required", False)]
            required_total = len(required_fields)
            required_present = 0

            field_map = {}
            if preview_form:
                for fld in preview_form.fields:
                    field_map[fld.field_id] = fld

            for field_def in required_fields:
                pf = field_map.get(field_def.field_id)
                missing = pf is None or pf.proposed_value in (None, "", " ")
                if missing:
                    form_checks.append(
                        ReadinessCheckResult(
                            code="missing_required_field",
                            severity=ReadinessSeverity.BLOCKER,
                            message=f"Required field {field_def.field_id} is missing",
                            field_id=field_def.field_id,
                            form_id=form_id,
                            evidence={"source": getattr(pf, "source_path", None)} if pf else {},
                        )
                    )
                    blockers += 1
                else:
                    required_present += 1
                    if pf.notes:
                        form_checks.append(
                            ReadinessCheckResult(
                                code="needs_confirmation",
                                severity=ReadinessSeverity.WARN,
                                message=f"Field {field_def.field_id} requires confirmation",
                                field_id=field_def.field_id,
                                form_id=form_id,
                                evidence={"note": pf.notes},
                            )
                        )
                        warnings += 1

            form_completion = int(round((required_present / required_total) * 100)) if required_total else 100

            summaries.append(
                FormReadinessSummary(
                    form_id=form_id,
                    title=definition.label,
                    completion_percent=form_completion,
                    missing_required_fields=required_total - required_present,
                    missing_required_documents=0,
                    checks=form_checks,
                )
            )
            total_required += required_total
            total_present += required_present

        overall_completion = int(round((total_present / total_required) * 100)) if total_required else 100
        return summaries, blockers, warnings, overall_completion, notes

    def _evaluate_documents(
        self,
        candidate: CandidateProfile,
        program_code: str,
        existing_docs: List[Document],
    ) -> Tuple[List[ReadinessCheckResult], List[str]]:
        results: List[ReadinessCheckResult] = []
        missing_docs: List[str] = []
        matrix = self.document_service.get_required_documents(candidate, program_code)
        existing_types = {d.document_type for d in existing_docs}
        for doc in matrix.required_documents:
            if doc.id not in existing_types:
                missing_docs.append(doc.id)
                results.append(
                    ReadinessCheckResult(
                        code="missing_required_document",
                        severity=ReadinessSeverity.BLOCKER,
                        message=f"Missing required document {doc.id}",
                        document_code=doc.id,
                        evidence={"category": doc.category},
                    )
                )
        return results, missing_docs

    def generate_report(
        self,
        *,
        case_id: str,
        bundle_id: str,
        tenant_id: str,
        db_session: Session,
        program_code: Optional[str] = None,
    ) -> SubmissionReadinessReport:
        repo = CaseRepository(db_session)
        case = repo.get_case(case_id, tenant_id=tenant_id)
        if not case:
            raise SubmissionReadinessError("Case not found or tenant mismatch")

        forms_by_id, bundle_forms, bundle_programs = self._load_forms_bundle(bundle_id)

        target_program = program_code or (bundle_programs[0] if bundle_programs else None)
        try:
            preview = self.autofill_engine.build_autofill_preview(
                case_id=case_id,
                program_code=target_program,
                bundle_id=bundle_id,
                tenant_id=tenant_id,
                db_session=db_session,
            )
        except FormAutofillEngineError as exc:
            raise SubmissionReadinessError(str(exc)) from exc

        preview_filtered = FormAutofillPreviewResult(
            bundle_id=preview.bundle_id,
            forms=[f for f in preview.forms if f.form_id in bundle_forms],
            warnings=preview.warnings,
        )

        form_summaries, blockers, warnings, overall_completion, notes = self._evaluate_forms(
            preview_filtered, forms_by_id
        )

        candidate = self._convert_profile(case.profile or {})
        documents = self._get_case_documents(db_session, case_id, tenant_id)
        doc_checks: List[ReadinessCheckResult] = []
        missing_docs: List[str] = []
        if target_program:
            doc_checks, missing_docs = self._evaluate_documents(candidate, target_program.lower(), documents)
            blockers += sum(1 for c in doc_checks if c.severity == ReadinessSeverity.BLOCKER)

        if form_summaries:
            form_summaries[0].checks.extend(doc_checks)
            form_summaries[0].missing_required_documents = len(missing_docs)

        status = "READY"
        if blockers > 0:
            status = "NOT_READY"
        elif warnings > 0:
            status = "NEEDS_REVIEW"

        return SubmissionReadinessReport(
            case_id=case_id,
            bundle_id=bundle_id,
            generated_at=datetime.utcnow(),
            overall_status=status,
            overall_completion_percent=overall_completion,
            blockers_count=blockers,
            warnings_count=warnings,
            forms=form_summaries,
            missing_documents=missing_docs,
            notes=notes,
        )

