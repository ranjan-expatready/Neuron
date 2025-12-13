from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.app.cases.repository import CaseRepository
from src.app.config.intake_config import clear_intake_config_cache
from src.app.services.intake_engine import IntakeEngine
from src.app.services.document import DocumentService


class SubmissionReadinessEngineError(Exception):
    """Base error for submission readiness evaluation."""


ENGINE_VERSION = "1.0.0"


class Blocker(BaseModel):
    code: str
    message: str
    config_refs: List[str] = Field(default_factory=list)
    source_refs: List[str] = Field(default_factory=list)
    rule_refs: List[str] = Field(default_factory=list)


class DocumentReadinessItem(BaseModel):
    id: str
    label: str
    category: str
    required: bool
    reasons: List[str] = Field(default_factory=list)
    uploaded: bool = False
    matched_document_ids: List[str] = Field(default_factory=list)
    config_ref: Optional[str] = None
    source_ref: Optional[str] = None
    unsourced: bool = False


class SubmissionReadinessResult(BaseModel):
    case_id: str
    tenant_id: str
    program_code: str
    status: str
    ready: bool
    missing_documents: List[str] = Field(default_factory=list)
    documents: List[DocumentReadinessItem] = Field(default_factory=list)
    blockers: List[Blocker] = Field(default_factory=list)
    explanations: List[str] = Field(default_factory=list)
    engine_version: str
    evaluation_timestamp: str
    config_hash: str
    source_bundle_version: str


class SubmissionReadinessEngine:
    """
    Read-only, config-driven submission readiness evaluator.
    Determines whether a case has the required documents for a program.
    """

    def __init__(self, base_path: Optional[str] = None) -> None:
        self.base_path = base_path
        # ensure deterministic config when tests override base_path
        clear_intake_config_cache()

    def _config_files(self) -> List[Path]:
        base = Path(self.base_path) if self.base_path else Path(__file__).resolve().parents[4] / "config" / "domain"
        candidates = [
            base / "documents.yaml",
            base / "fields.yaml",
            base / "intake_templates.yaml",
            base / "forms.yaml",
        ]
        return [p for p in candidates if p.exists()]

    def _config_hash(self) -> str:
        h = hashlib.sha256()
        for path in sorted(self._config_files(), key=lambda p: p.name):
            h.update(path.name.encode("utf-8"))
            h.update(path.read_bytes())
        return h.hexdigest()

    def _resolve_program(self, case, explicit_program: Optional[str]) -> str:
        if explicit_program:
            return explicit_program
        if isinstance(case.program_eligibility, dict):
            results = case.program_eligibility.get("results")
            if isinstance(results, list):
                eligible_codes = [
                    item.get("program_code")
                    for item in results
                    if isinstance(item, dict) and item.get("eligible")
                ]
                unique_codes = sorted({c for c in eligible_codes if c})
                if len(unique_codes) == 1:
                    return unique_codes[0]
                if len(unique_codes) > 1:
                    raise SubmissionReadinessEngineError("Program inference ambiguous")
        raise SubmissionReadinessEngineError("Program code is required for submission readiness")

    def evaluate_case(
        self,
        case_id: str,
        tenant_id: str,
        program_code: Optional[str] = None,
        db_session: Session = None,
    ) -> SubmissionReadinessResult:
        repo = CaseRepository(db_session)
        case = repo.get_case(str(case_id), tenant_id=str(tenant_id))
        if not case:
            raise SubmissionReadinessEngineError("Case not found")

        resolved_program = self._resolve_program(case, program_code)

        intake_engine = IntakeEngine(base_path=self.base_path)
        checklist = intake_engine.get_document_checklist_for_case(
            case, program_code=resolved_program, db_session=db_session
        )

        uploaded_docs = DocumentService.get_documents_by_case(
            db_session, str(tenant_id), str(case_id)
        )

        documents_readiness: List[DocumentReadinessItem] = []
        missing: List[str] = []
        explanations: List[str] = []
        blockers: List[Blocker] = []

        for requirement in sorted(checklist, key=lambda r: (r.id, r.category)):
            matched = [
                doc
                for doc in uploaded_docs
                if doc.document_type == requirement.id or doc.category == requirement.category
            ]
            unsourced = not bool(requirement.source_ref)
            item = DocumentReadinessItem(
                id=requirement.id,
                label=requirement.label,
                category=requirement.category,
                required=requirement.required,
                reasons=requirement.reasons,
                uploaded=bool(matched),
                matched_document_ids=[doc.id for doc in matched],
                config_ref=requirement.config_ref
                or f"config/domain/documents.yaml#{requirement.id}",
                source_ref=requirement.source_ref or "UNSOURCED",
                unsourced=unsourced,
            )
            documents_readiness.append(item)
            if requirement.required and not unsourced and not matched:
                missing.append(requirement.id)
                explanations.append(f"Missing required document: {requirement.id}")
                blockers.append(
                    Blocker(
                        code="missing_required_document",
                        message=f"Document {requirement.id} is required",
                        config_refs=[item.config_ref] if item.config_ref else [],
                        source_refs=[item.source_ref] if item.source_ref else [],
                        rule_refs=[],
                    )
                )
            if unsourced:
                explanations.append(f"UNSOURCED requirement: {requirement.id}")

        ready = len(missing) == 0
        status = "READY" if ready else "NOT_READY"

        return SubmissionReadinessResult(
            case_id=str(case_id),
            tenant_id=str(tenant_id),
            program_code=resolved_program,
            status=status,
            ready=ready,
            missing_documents=missing,
            documents=documents_readiness,
            blockers=sorted(blockers, key=lambda b: b.code),
            explanations=sorted(explanations),
            engine_version=ENGINE_VERSION,
            evaluation_timestamp=datetime.now(timezone.utc).isoformat(),
            config_hash=self._config_hash(),
            source_bundle_version="unknown",
        )


__all__ = [
    "SubmissionReadinessEngine",
    "SubmissionReadinessEngineError",
    "SubmissionReadinessResult",
    "DocumentReadinessItem",
]

