from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.app.cases.models_db import CaseEvent, CaseRecord, CaseSnapshot


class CaseRepository:
    """CRUD helpers for CaseRecord."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_case(
        self,
        *,
        profile: dict[str, Any],
        program_eligibility: dict[str, Any],
        crs_breakdown: Optional[dict[str, Any]],
        required_artifacts: Optional[dict[str, Any]],
        config_fingerprint: Optional[dict[str, Any]],
        source: str,
        status: str = "draft",
        tenant_id: Optional[str] = None,
        created_by: Optional[str] = "system",
        created_by_user_id: Optional[str] = None,
        case_type: str = "express_entry_basic",
    ) -> CaseRecord:
        record = CaseRecord(
            profile=profile,
            program_eligibility=program_eligibility,
            crs_breakdown=crs_breakdown,
            required_artifacts=required_artifacts,
            config_fingerprint=config_fingerprint,
            source=source,
            status=status,
            tenant_id=tenant_id,
            created_by_user_id=created_by_user_id,
            created_by=created_by,
            case_type=case_type,
        )
        self.db.add(record)
        self.db.flush()
        return record

    def get_case(self, case_id: str, tenant_id: Optional[str] = None) -> Optional[CaseRecord]:
        query = self.db.query(CaseRecord).filter(CaseRecord.id == case_id)
        if tenant_id:
            query = query.filter(CaseRecord.tenant_id == tenant_id)
        return query.first()

    def list_recent(self, limit: int = 50) -> list[CaseRecord]:
        return self.db.query(CaseRecord).order_by(CaseRecord.created_at.desc()).limit(limit).all()

    def list_recent_for_tenant(self, tenant_id: str, limit: int = 50) -> list[CaseRecord]:
        return (
            self.db.query(CaseRecord)
            .filter(CaseRecord.tenant_id == tenant_id)
            .order_by(CaseRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    def count_active_cases(self, tenant_id: str) -> int:
        return (
            self.db.query(CaseRecord)
            .filter(CaseRecord.tenant_id == tenant_id, CaseRecord.status != "archived")
            .count()
        )


class CaseSnapshotRepository:
    """Immutable snapshots per evaluation."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def next_version(self, case_id: str) -> int:
        current = (
            self.db.query(func.max(CaseSnapshot.version))
            .filter(CaseSnapshot.case_id == case_id)
            .scalar()
        )
        return (current or 0) + 1

    def create_snapshot(
        self,
        *,
        case_id: str,
        version: int,
        profile: dict[str, Any],
        program_eligibility: dict[str, Any],
        crs_breakdown: Optional[dict[str, Any]],
        required_artifacts: Optional[dict[str, Any]],
        config_fingerprint: Optional[dict[str, Any]],
        source: str,
        snapshot_at: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
        case_type: str = "express_entry_basic",
    ) -> CaseSnapshot:
        snapshot = CaseSnapshot(
            case_id=case_id,
            version=version,
            profile=profile,
            program_eligibility=program_eligibility,
            crs_breakdown=crs_breakdown,
            required_artifacts=required_artifacts,
            config_fingerprint=config_fingerprint,
            source=source,
            snapshot_at=snapshot_at,
            tenant_id=tenant_id,
            case_type=case_type,
        )
        self.db.add(snapshot)
        self.db.flush()
        return snapshot

    def list_snapshots(self, case_id: str) -> list[CaseSnapshot]:
        return (
            self.db.query(CaseSnapshot)
            .filter(CaseSnapshot.case_id == case_id)
            .order_by(CaseSnapshot.version.asc())
            .all()
        )


class CaseEventRepository:
    """Audit events for case evaluations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def log_event(
        self,
        *,
        event_type: str,
        case_id: Optional[str],
        actor: str,
        tenant_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> CaseEvent:
        event = CaseEvent(
            event_type=event_type,
            case_id=case_id,
            actor=actor,
            tenant_id=tenant_id,
            event_metadata=metadata or {},
        )
        self.db.add(event)
        self.db.flush()
        return event

    def list_events(self, case_id: str) -> list[CaseEvent]:
        return (
            self.db.query(CaseEvent)
            .filter(CaseEvent.case_id == case_id)
            .order_by(CaseEvent.created_at.asc())
            .all()
        )

