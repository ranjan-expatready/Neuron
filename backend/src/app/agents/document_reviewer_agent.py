from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from src.app.models.case import Case
from src.app.services.agent_orchestrator import AgentOrchestratorService
from src.app.services.document import DocumentService
from src.app.services.intake_engine import IntakeEngine, DocumentRequirementResolved
from src.app.cases.repository import CaseRepository


class DocumentReviewerAgent:
    """
    Shadow-only document reviewer.
    Uses existing document matrix + case documents to suggest completeness findings.
    No OCR, no external sends, no state mutation.
    """

    def __init__(self, orchestrator: AgentOrchestratorService, intake_engine: Optional[IntakeEngine] = None):
        self.orchestrator = orchestrator
        self.intake_engine = intake_engine or IntakeEngine()

    def _get_case_context(self, db: Session, case_id: str, tenant_id: Optional[str]) -> dict:
        """
        Try to load a lifecycle Case (has org_id) first; if not found, fall back to CaseRecord.
        """
        lifecycle_case = (
            db.query(Case)
            .filter(Case.id == case_id, Case.deleted_at.is_(None))
            .filter(Case.org_id == tenant_id if tenant_id else True)
            .first()
        )
        if lifecycle_case:
            return {
                "program_code": lifecycle_case.case_type,
                "profile": lifecycle_case.form_data or {},
                "case_id": lifecycle_case.id,
                "org_id": lifecycle_case.org_id,
            }

        repo = CaseRepository(db)
        record = repo.get_case(case_id, tenant_id=tenant_id)
        if not record:
            raise ValueError("Case not found or access denied")
        return {
            "program_code": None,
            "profile": record.profile or {},
            "case_id": record.id,
            "org_id": tenant_id,
            "record": record,
        }

    def _resolve_program(self, case_program: Optional[str], program_code: Optional[str], record=None) -> str:
        if program_code:
            return program_code
        if case_program:
            return case_program
        if record:
            inferred = self.intake_engine._infer_program_from_case(record)  # pylint: disable=protected-access
            if inferred:
                return inferred
        raise ValueError("Program code is required to review documents")

    @staticmethod
    def _group_documents(documents) -> Dict[str, list]:
        grouped: Dict[str, list] = defaultdict(list)
        for doc in documents:
            grouped[doc.document_type].append(doc)
        return grouped

    def review_case(
        self,
        case_id: str,
        tenant_id: str,
        db_session: Session,
        program_code: Optional[str] = None,
        created_by_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        ctx = self._get_case_context(db_session, case_id, tenant_id)
        resolved_program = self._resolve_program(ctx.get("program_code"), program_code, ctx.get("record"))

        profile_data = ctx.get("profile") or {}
        checklist: List[DocumentRequirementResolved] = self.intake_engine.get_document_checklist_for_profile(
            profile_data, resolved_program, db_session=None
        )

        documents = []
        if ctx.get("org_id") and ctx.get("case_id"):
            documents = DocumentService.get_documents_by_case(
                db_session, org_id=ctx["org_id"], case_id=ctx["case_id"]
            )
        docs_by_type = self._group_documents(documents)

        required_present: List[Dict[str, Any]] = []
        required_missing: List[Dict[str, Any]] = []
        optional_present: List[Dict[str, Any]] = []
        duplicates: List[Dict[str, Any]] = []
        unmatched: List[Dict[str, Any]] = []

        checklist_ids = {c.id for c in checklist}

        for requirement in checklist:
            matched_docs = docs_by_type.get(requirement.id, [])
            entry = {
                "requirement_id": requirement.id,
                "label": requirement.label,
                "category": requirement.category,
                "document_ids": [doc.id for doc in matched_docs],
                "filenames": [doc.filename for doc in matched_docs],
            }
            if requirement.required:
                if matched_docs:
                    required_present.append(entry)
                else:
                    required_missing.append(entry)
            else:
                if matched_docs:
                    optional_present.append(entry)

        for doc_type, items in docs_by_type.items():
            if len(items) > 1:
                duplicates.append(
                    {
                        "document_type": doc_type,
                        "document_ids": [d.id for d in items],
                        "filenames": [d.filename for d in items],
                    }
                )
            if doc_type not in checklist_ids:
                unmatched.extend(
                    [{"document_type": doc_type, "document_id": d.id, "filename": d.filename} for d in items]
                )

        findings = {
            "program_code": resolved_program,
            "case_id": case_id,
            "findings": {
                "required_present": required_present,
                "required_missing": required_missing,
                "optional_present": optional_present,
                "duplicates": duplicates,
                "unmatched": unmatched,
            },
        }

        session = self.orchestrator.create_session(
            agent_name="document_reviewer",
            tenant_id=tenant_id,
            case_id=case_id,
            created_by_user_id=created_by_user_id,
            context={"program_code": resolved_program},
        )
        action = self.orchestrator.record_action(
            agent_name="document_reviewer",
            action_type="document_review_suggestion",
            payload=findings,
            status="suggested",
            tenant_id=tenant_id,
            case_id=case_id,
            session_id=session.id,
            auto_mode=False,
        )

        return {
            "program_code": resolved_program,
            "case_id": case_id,
            "findings": findings["findings"],
            "agent_action_id": action.id,
            "agent_session_id": session.id,
        }

