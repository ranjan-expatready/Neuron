from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from src.app.cases.repository import CaseRepository
from src.app.config.form_config import (
    FormBundleDefinition,
    FormDefinition,
    load_form_bundles,
    load_form_definitions,
)
from src.app.domain.forms.models import (
    AttachmentPlan,
    FieldPrepResult,
    FormPrepResult,
    ReadinessGap,
    SubmissionPrepResult,
)
from src.app.models.document import Document
from src.app.services.form_autofill_engine import FormAutofillEngine


class SubmissionPrepEngineError(Exception):
    """Base error for submission preparation engine."""


class SubmissionPrepEngine:
    """
    Deterministic, read-only engine that assembles a submission-ready package
    using existing canonical profile data, form definitions, and readiness results.
    Shadow-only: no DB mutations, no external calls, no file operations.
    """

    def __init__(self, base_path: Optional[str] = None):
        self._base_path = base_path
        self._autofill_engine = FormAutofillEngine(base_path=base_path)

    def _load_form_bundle(self, bundle_id: Optional[str], program_code: Optional[str]) -> Optional[FormBundleDefinition]:
        """Load form bundle by ID or select by program code."""
        try:
            bundles = load_form_bundles(base_path=self._base_path)
        except Exception:
            bundles = []

        # If bundle_id specified, find exact match
        if bundle_id:
            for bundle in bundles:
                if bundle.id == bundle_id:
                    return bundle

        # Otherwise, find bundle by program code or use default (first active bundle)
        if program_code:
            for bundle in bundles:
                if program_code in bundle.program_codes and bundle.status == "active":
                    return bundle

        # Default: first active bundle
        for bundle in bundles:
            if bundle.status == "active":
                return bundle

        return None

    def _get_case_profile(self, db_session: Session, case_id: str, tenant_id: str) -> Dict[str, Any]:
        """Get canonical profile for case."""
        repo = CaseRepository(db_session)
        record = repo.get_case(case_id, tenant_id=tenant_id)
        if not record:
            raise SubmissionPrepEngineError("Case not found or tenant mismatch")
        profile = record.profile or {}
        if "profile" not in profile:
            profile = {"profile": profile}
        return profile

    def _get_case_documents(self, db_session: Session, case_id: str, tenant_id: str) -> List[Document]:
        """Get documents for case."""
        return (
            db_session.query(Document)
            .filter(Document.case_id == case_id, Document.org_id == tenant_id)
            .all()
        )

    def _get_form_definitions(self) -> Dict[str, FormDefinition]:
        """Load form definitions indexed by ID."""
        try:
            forms = load_form_definitions(base_path=self._base_path)
            return {f.id: f for f in forms}
        except Exception:
            return {}

    def _compute_readiness_gaps(
        self,
        bundle: FormBundleDefinition,
        profile: Dict[str, Any],
        documents: List[Document],
        form_definitions: Dict[str, FormDefinition]
    ) -> List[ReadinessGap]:
        """Compute readiness gaps based on required documents and forms."""
        gaps: List[ReadinessGap] = []

        # Check required documents for each form in bundle
        for form_id in bundle.forms:
            form_def = form_definitions.get(form_id)
            if not form_def:
                gaps.append(ReadinessGap(
                    gap_type="incomplete_form",
                    description=f"Form definition not found: {form_id}",
                    severity="blocking",
                    related_form=form_id
                ))
                continue

            # Check if form requires attachments (based on document mappings in autofill)
            # For now, assume forms requiring document fields need attachments
            has_document_fields = any(
                field.field_id for field in form_def.fields
                if any(mapping.source_type == "document"
                      for mapping in [] if hasattr(mapping, 'source_type'))  # Placeholder
            )

            if has_document_fields:
                # Find documents that could satisfy this form's requirements
                # This is a simplified check - in real implementation would use document matrix
                relevant_docs = [
                    doc for doc in documents
                    if any(keyword in (doc.document_type or "").lower()
                          for keyword in form_id.lower().split("_"))
                ]
                if not relevant_docs:
                    gaps.append(ReadinessGap(
                        gap_type="missing_document",
                        description=f"No relevant documents found for form {form_id}",
                        severity="blocking",
                        related_form=form_id
                    ))

        return gaps

    def _build_form_prep_results(
        self,
        autofill_result: Any,  # FormAutofillPreviewResult
        form_definitions: Dict[str, FormDefinition]
    ) -> List[FormPrepResult]:
        """Build form preparation results from autofill data."""
        results: List[FormPrepResult] = []

        for form_result in autofill_result.forms:
            form_id = form_result.form_id
            form_def = form_definitions.get(form_id)

            field_prep_results: List[FieldPrepResult] = []
            unresolved_count = 0

            for field in form_result.fields:
                # Map autofill field to prep result
                if field.proposed_value is not None:
                    status = "resolved"
                    source = "autofill_mapping"
                    reason = None
                else:
                    status = "unresolved"
                    source = "not_resolved"
                    reason = field.notes or "No value resolved"
                    unresolved_count += 1

                # Get field name from definition if available
                field_name = field.field_id
                if form_def:
                    for f_def in form_def.fields:
                        if f_def.field_id == field.field_id:
                            field_name = f_def.label or field_name
                            break

                field_prep_results.append(FieldPrepResult(
                    field_code=field.field_id,
                    field_name=field_name,
                    resolved_value=field.proposed_value,
                    source=source,
                    status=status,
                    reason=reason
                ))

            # Determine form status
            if unresolved_count == 0:
                form_status = "resolved"
            elif unresolved_count < len(field_prep_results):
                form_status = "partial"
            else:
                form_status = "unresolved"

            # Check if form requires attachments (simplified)
            attachment_required = any(
                field.resolved_value and isinstance(field.resolved_value, dict)
                and "document_id" in field.resolved_value
                for field in field_prep_results
            )

            results.append(FormPrepResult(
                form_code=form_id,
                form_name=form_def.label if form_def else form_id,
                fields=field_prep_results,
                attachment_required=attachment_required,
                status=form_status
            ))

        return results

    def _build_attachment_plan(
        self,
        bundle: FormBundleDefinition,
        documents: List[Document],
        form_prep_results: List[FormPrepResult]
    ) -> List[AttachmentPlan]:
        """Build document attachment plan based on form requirements."""
        plans: List[AttachmentPlan] = []

        for form_result in form_prep_results:
            if not form_result.attachment_required:
                continue

            # Find documents that could be attached to this form
            # This is a simplified mapping - real implementation would use document matrix
            attached_docs = []
            missing_reason = None

            # Look for documents that match form keywords
            form_keywords = form_result.form_code.lower().split("_")
            for doc in documents:
                doc_type_lower = (doc.document_type or "").lower()
                if any(keyword in doc_type_lower for keyword in form_keywords):
                    attached_docs.append(doc.id)

            if not attached_docs:
                missing_reason = f"No documents found matching form requirements for {form_result.form_code}"

            plans.append(AttachmentPlan(
                document_type=form_result.form_code,
                required_for_form=form_result.form_code,
                attached_document_ids=attached_docs,
                status="attached" if attached_docs else "missing",
                reason=missing_reason
            ))

        return plans

    def prepare_submission(
        self,
        *,
        case_id: str,
        program_code: Optional[str] = None,
        bundle_id: Optional[str] = None,
        tenant_id: str,
        db_session: Session,
    ) -> SubmissionPrepResult:
        """
        Prepare a deterministic submission package for the given case.
        Returns a comprehensive view of what would be submitted to IRCC.
        """
        # Load form bundle
        bundle = self._load_form_bundle(bundle_id, program_code)
        if not bundle:
            raise SubmissionPrepEngineError("No suitable form bundle found")

        # Get case data
        profile = self._get_case_profile(db_session, case_id, tenant_id)
        documents = self._get_case_documents(db_session, case_id, tenant_id)
        form_definitions = self._get_form_definitions()

        # Get autofill results
        autofill_result = self._autofill_engine.build_autofill_preview(
            case_id=case_id,
            program_code=program_code,
            tenant_id=tenant_id,
            db_session=db_session,
        )

        # Build form preparation results
        form_prep_results = self._build_form_prep_results(autofill_result, form_definitions)

        # Build attachment plan
        attachment_plans = self._build_attachment_plan(bundle, documents, form_prep_results)

        # Compute readiness gaps
        blocking_gaps = self._compute_readiness_gaps(bundle, profile, documents, form_definitions)

        # Build reasons list
        reasons = []
        if blocking_gaps:
            reasons.append(f"Found {len(blocking_gaps)} readiness gaps")
        unresolved_forms = [f for f in form_prep_results if f.status == "unresolved"]
        if unresolved_forms:
            reasons.append(f"{len(unresolved_forms)} forms have unresolved fields")

        # Determine summary readiness
        has_blocking_gaps = any(gap.severity == "blocking" for gap in blocking_gaps)
        has_unresolved_forms = any(form.status == "unresolved" for form in form_prep_results)
        has_missing_attachments = any(plan.status == "missing" for plan in attachment_plans)
        summary_ready = not (has_blocking_gaps or has_unresolved_forms or has_missing_attachments)

        return SubmissionPrepResult(
            case_id=case_id,
            program_code=program_code,
            form_bundle_id=bundle.id,
            forms=form_prep_results,
            document_attachments=attachment_plans,
            blocking_gaps=blocking_gaps,
            summary_ready=summary_ready,
            generated_at=datetime.utcnow(),
            reasons=reasons,
        )
