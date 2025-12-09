from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, Tuple

from sqlalchemy.orm import Session

from src.app.cases.models_db import CaseRecord
from src.app.cases.repository import (
    CaseEventRepository,
    CaseRepository,
    CaseSnapshotRepository,
)


class CaseLifecycleError(Exception):
    """Domain error for invalid lifecycle operations."""


class CaseLifecycleService:
    """Tenant-aware case lifecycle with audit + snapshots."""

    ALLOWED_TRANSITIONS = {
        "draft": {"submitted", "archived"},
        "submitted": {"in_review", "archived"},
        "in_review": {"complete", "archived"},
        "complete": {"archived"},
        "archived": set(),
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.case_repo = CaseRepository(db)
        self.snapshot_repo = CaseSnapshotRepository(db)
        self.event_repo = CaseEventRepository(db)

    def _transition(
        self,
        *,
        case_id: str,
        tenant_id: str,
        user_id: str,
        new_status: str,
        event_type: str,
    ) -> Tuple[CaseRecord, int]:
        record = self.case_repo.get_case(case_id, tenant_id=tenant_id)
        if not record:
            raise CaseLifecycleError("Case not found for tenant")

        current = record.status
        allowed = self.ALLOWED_TRANSITIONS.get(current, set())
        if new_status not in allowed:
            raise CaseLifecycleError(f"Cannot transition from {current} to {new_status}")

        record.status = new_status
        record.updated_at = datetime.utcnow()
        record.created_by_user_id = record.created_by_user_id or user_id

        next_version = self.snapshot_repo.next_version(record.id)
        self.snapshot_repo.create_snapshot(
            case_id=record.id,
            version=next_version,
            profile=record.profile or {},
            program_eligibility=record.program_eligibility or {},
            crs_breakdown=record.crs_breakdown,
            required_artifacts=record.required_artifacts,
            config_fingerprint=record.config_fingerprint,
            source=record.source,
            tenant_id=record.tenant_id,
        )

        self.event_repo.log_event(
            event_type=event_type,
            case_id=record.id,
            tenant_id=record.tenant_id,
            actor=user_id,
            metadata={"from": current, "to": new_status},
        )

        self.db.commit()
        self.db.refresh(record)
        return record, next_version

    def create_case(
        self,
        *,
        profile: Optional[dict[str, Any]] = None,
        program_eligibility: Optional[dict[str, Any]] = None,
        crs_breakdown: Optional[dict[str, Any]] = None,
        required_artifacts: Optional[dict[str, Any]] = None,
        config_fingerprint: Optional[dict[str, Any]] = None,
        tenant_id: str,
        user_id: str,
        source: str = "case_lifecycle",
    ) -> CaseRecord:
        record = self.case_repo.create_case(
            profile=profile or {},
            program_eligibility=program_eligibility or {},
            crs_breakdown=crs_breakdown or {},
            required_artifacts=required_artifacts or {},
            config_fingerprint=config_fingerprint or {},
            source=source,
            status="draft",
            tenant_id=tenant_id,
            created_by=user_id,
            created_by_user_id=user_id,
        )

        version = self.snapshot_repo.next_version(record.id)
        self.snapshot_repo.create_snapshot(
            case_id=record.id,
            version=version,
            profile=record.profile,
            program_eligibility=record.program_eligibility,
            crs_breakdown=record.crs_breakdown,
            required_artifacts=record.required_artifacts,
            config_fingerprint=record.config_fingerprint,
            source=record.source,
            tenant_id=record.tenant_id,
        )

        self.event_repo.log_event(
            event_type="CASE_CREATED",
            case_id=record.id,
            tenant_id=record.tenant_id,
            actor=user_id,
            metadata={"status": "draft"},
        )

        self.db.commit()
        self.db.refresh(record)
        return record

    def submit_case(self, case_id: str, user_id: str, tenant_id: str) -> CaseRecord:
        record, _ = self._transition(
            case_id=case_id,
            tenant_id=tenant_id,
            user_id=user_id,
            new_status="submitted",
            event_type="CASE_SUBMITTED",
        )
        return record

    def mark_in_review(self, case_id: str, user_id: str, tenant_id: str) -> CaseRecord:
        record, _ = self._transition(
            case_id=case_id,
            tenant_id=tenant_id,
            user_id=user_id,
            new_status="in_review",
            event_type="CASE_IN_REVIEW",
        )
        return record

    def mark_complete(self, case_id: str, user_id: str, tenant_id: str) -> CaseRecord:
        record, _ = self._transition(
            case_id=case_id,
            tenant_id=tenant_id,
            user_id=user_id,
            new_status="complete",
            event_type="CASE_COMPLETE",
        )
        return record

    def archive_case(self, case_id: str, user_id: str, tenant_id: str) -> CaseRecord:
        record, _ = self._transition(
            case_id=case_id,
            tenant_id=tenant_id,
            user_id=user_id,
            new_status="archived",
            event_type="CASE_ARCHIVED",
        )
        return record

