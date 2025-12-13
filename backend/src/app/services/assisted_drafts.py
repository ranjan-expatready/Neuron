from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.app.cases.models_db import CaseRecord
from src.app.cases.repository import CaseRepository
from src.app.models.tenant import Tenant
from src.app.services.submission_preparation import (
    AutomationReadiness,
    SubmissionPreparationPackage,
    SubmissionPreparationService,
    SubmissionPreparationServiceError,
)


class AssistedDraftsError(Exception):
    def __init__(self, message: str, status_code: int = 400, reason: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.reason = reason or message


class DraftChecklist(BaseModel):
    label: str = "DRAFT – Human Review Required"
    forms_ready: List[str] = Field(default_factory=list)
    attachments_ready: List[str] = Field(default_factory=list)
    blocking_gaps: List[str] = Field(default_factory=list)
    is_draft: bool = True


class DraftCaseSummary(BaseModel):
    label: str = "DRAFT – Case Summary (Human Review Required)"
    program_code: str
    readiness_verdict: str
    preparation_hash: Optional[str] = None
    summary_lines: List[str] = Field(default_factory=list)
    is_draft: bool = True


class DraftInternalNotes(BaseModel):
    label: str = "DRAFT – Internal Review Notes"
    assumptions: List[str] = Field(default_factory=list)
    evidence_sources: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)
    is_draft: bool = True


class AssistedDraftBundle(BaseModel):
    bundle_version: str = "v1"
    case_id: str
    tenant_id: str
    is_draft: bool = True
    automation_readiness_ref: AutomationReadiness
    generated_at: str
    drafts: dict
    audit: dict


class AssistedDraftService:
    def __init__(
        self,
        *,
        prep_service: Optional[SubmissionPreparationService] = None,
    ) -> None:
        self.prep_service = prep_service or SubmissionPreparationService()

    def _tenant_policy_enabled(self, db_session: Session, tenant_id: str) -> bool:
        tenant: Optional[Tenant] = db_session.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise AssistedDraftsError("Tenant not found", status_code=404, reason="tenant_not_found")
        metadata = tenant.tenant_metadata or {}
        return bool(metadata.get("assisted_automation_enabled", False))

    def _validate_preconditions(
        self,
        *,
        package: SubmissionPreparationPackage,
        policy_enabled: bool,
    ) -> AutomationReadiness:
        auto = package.automation_readiness
        if not policy_enabled:
            raise AssistedDraftsError(
                "Assisted automation disabled by tenant policy",
                status_code=403,
                reason="assisted_automation_disabled",
            )
        if not auto.automation_eligible:
            raise AssistedDraftsError(
                "Automation readiness not eligible",
                status_code=412,
                reason=";".join(auto.blocking_reasons or ["automation_not_eligible"]),
            )
        return auto

    def _build_checklist(self, package: SubmissionPreparationPackage) -> DraftChecklist:
        forms_ready = [f.form_code for f in package.forms]
        attachments_ready = [
            att.doc_code for att in (package.forms[0].attachments if package.forms else []) if att.status == "available"
        ]
        blocking_gaps = package.gaps_summary.blocking or []
        return DraftChecklist(
            forms_ready=forms_ready,
            attachments_ready=attachments_ready,
            blocking_gaps=blocking_gaps,
        )

    def _build_case_summary(self, package: SubmissionPreparationPackage) -> DraftCaseSummary:
        readiness_verdict = package.readiness_reference.get("readiness_verdict")
        summary_lines = [
            f"Program: {package.program_code}",
            f"Readiness verdict: {readiness_verdict}",
            f"Gaps (blocking/non-blocking): {len(package.gaps_summary.blocking)}/{len(package.gaps_summary.non_blocking)}",
        ]
        return DraftCaseSummary(
            program_code=package.program_code,
            readiness_verdict=readiness_verdict,
            preparation_hash=package.deterministic_hash,
            summary_lines=summary_lines,
        )

    def _build_internal_notes(
        self,
        package: SubmissionPreparationPackage,
        auto: AutomationReadiness,
    ) -> DraftInternalNotes:
        assumptions: List[str] = []
        if auto.blocking_reasons:
            assumptions.append("Automation readiness previously evaluated; no blocking reasons recorded.")
        evidence_sources = [cfg for cfg in package.audit.get("consulted_configs", [])]
        risk_flags: List[str] = []
        return DraftInternalNotes(
            assumptions=assumptions or ["Assisted automation is draft-only. Human review required."],
            evidence_sources=evidence_sources,
            risk_flags=risk_flags,
        )

    def build_drafts(
        self,
        *,
        case_id: str,
        tenant_id: str,
        db_session: Session,
        program_code: Optional[str] = None,
    ) -> AssistedDraftBundle:
        repo = CaseRepository(db_session)
        case: Optional[CaseRecord] = repo.get_case(case_id, tenant_id=tenant_id)
        if not case:
            raise AssistedDraftsError("Case not found", status_code=404, reason="case_not_found")

        try:
            package = self.prep_service.build_package(
                case_id=case_id, tenant_id=tenant_id, program_code=program_code, db_session=db_session
            )
        except SubmissionPreparationServiceError as exc:
            raise AssistedDraftsError(str(exc), status_code=400) from exc

        policy_enabled = self._tenant_policy_enabled(db_session, tenant_id)
        auto = self._validate_preconditions(package=package, policy_enabled=policy_enabled)

        checklist = self._build_checklist(package)
        case_summary = self._build_case_summary(package)
        internal_notes = self._build_internal_notes(package, auto)

        return AssistedDraftBundle(
            case_id=case_id,
            tenant_id=tenant_id,
            automation_readiness_ref=auto,
            generated_at=datetime.now(timezone.utc).isoformat(),
            drafts={
                "checklist": checklist,
                "case_summary": case_summary,
                "internal_review_notes": internal_notes,
            },
            audit={
                "engine_versions": package.engine_versions,
                "config_refs": package.audit.get("consulted_configs", []),
                "policy_state": {"assisted_automation_enabled": policy_enabled},
            },
        )

