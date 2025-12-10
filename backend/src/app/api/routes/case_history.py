from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_current_user
from src.app.cases.repository import CaseEventRepository, CaseRepository, CaseSnapshotRepository
from src.app.db.database import get_db
from src.app.models.user import User
from src.app.security.errors import ForbiddenError, TenantAccessError

router = APIRouter()


class CaseSummary(BaseModel):
    id: str
    created_at: datetime
    source: str
    status: str
    programs: list[str] = Field(default_factory=list)
    crs_total: int | None = None


class CaseRecordResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    source: str
    status: str
    profile: dict[str, Any]
    program_eligibility: dict[str, Any]
    crs_breakdown: dict[str, Any] | None = None
    required_artifacts: dict[str, Any] | None = None
    config_fingerprint: dict[str, Any] | None = None
    tenant_id: str | None = None
    created_by: str | None = None


class CaseSnapshotResponse(BaseModel):
    id: str
    case_id: str
    snapshot_at: datetime
    source: str
    version: int
    profile: dict[str, Any]
    program_eligibility: dict[str, Any]
    crs_breakdown: dict[str, Any] | None = None
    required_artifacts: dict[str, Any] | None = None
    config_fingerprint: dict[str, Any] | None = None


class CaseEventResponse(BaseModel):
    id: str
    event_type: str
    created_at: datetime
    actor: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    case_id: str | None = None


class CaseDetailResponse(BaseModel):
    record: CaseRecordResponse
    snapshots: list[CaseSnapshotResponse]
    events: list[CaseEventResponse]


def _extract_programs(program_eligibility: Any) -> list[str]:
    if not isinstance(program_eligibility, dict):
        return []
    results = program_eligibility.get("results", [])
    if not isinstance(results, list):
        return []
    codes: list[str] = []
    for res in results:
        if isinstance(res, dict) and res.get("program_code"):
            codes.append(str(res["program_code"]))
    return codes


def _crs_total(crs_breakdown: Any) -> int | None:
    if not isinstance(crs_breakdown, dict):
        return None
    if isinstance(crs_breakdown.get("total"), (int, float)):
        return int(crs_breakdown["total"])
    if isinstance(crs_breakdown.get("total_points"), (int, float)):
        return int(crs_breakdown["total_points"])
    breakdown = crs_breakdown.get("breakdown")
    if isinstance(breakdown, dict):
        total = sum(v for v in breakdown.values() if isinstance(v, (int, float)))
        return int(total)
    return None


@router.get("", response_model=list[CaseSummary])
async def list_cases(
    limit: int = Query(50, ge=1, le=200),
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.tenant_id:
        raise TenantAccessError("Tenant context required")
    if include_deleted and current_user.role not in ("admin", "owner"):
        raise ForbiddenError("Only admin/owner may view deleted cases")
    repo = CaseRepository(db)
    records = repo.list_recent(limit=limit, tenant_id=current_user.tenant_id)
    summaries: list[CaseSummary] = []
    for record in records:
        summaries.append(
            CaseSummary(
                id=record.id,
                created_at=record.created_at,
                source=record.source,
                status=record.status,
                programs=_extract_programs(record.program_eligibility),
                crs_total=_crs_total(record.crs_breakdown),
            )
        )
    return summaries


@router.get("/{case_id}", response_model=CaseDetailResponse)
async def get_case(
    case_id: str,
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.tenant_id:
        raise TenantAccessError("Tenant context required")
    if include_deleted and current_user.role not in ("admin", "owner"):
        raise ForbiddenError("Only admin/owner may view deleted cases")

    repo = CaseRepository(db)
    snapshot_repo = CaseSnapshotRepository(db)
    event_repo = CaseEventRepository(db)

    record = repo.get_case(case_id, tenant_id=current_user.tenant_id, include_deleted=include_deleted)
    if not record or (record.is_deleted and not include_deleted):
        raise HTTPException(status_code=404, detail="Case not found")

    snapshots = snapshot_repo.list_snapshots(
        case_id, include_deleted=include_deleted, tenant_id=current_user.tenant_id
    )
    events = event_repo.list_events(case_id, include_deleted=include_deleted, tenant_id=current_user.tenant_id)

    return CaseDetailResponse(
        record=CaseRecordResponse(
            id=record.id,
            created_at=record.created_at,
            updated_at=record.updated_at,
            source=record.source,
            status=record.status,
            profile=record.profile,
            program_eligibility=record.program_eligibility,
            crs_breakdown=record.crs_breakdown,
            required_artifacts=record.required_artifacts,
            config_fingerprint=record.config_fingerprint,
            tenant_id=record.tenant_id,
            created_by=record.created_by,
        ),
        snapshots=[
            CaseSnapshotResponse(
                id=snapshot.id,
                case_id=snapshot.case_id,
                snapshot_at=snapshot.snapshot_at,
                source=snapshot.source,
                version=snapshot.version,
                profile=snapshot.profile,
                program_eligibility=snapshot.program_eligibility,
                crs_breakdown=snapshot.crs_breakdown,
                required_artifacts=snapshot.required_artifacts,
                config_fingerprint=snapshot.config_fingerprint,
            )
            for snapshot in snapshots
        ],
        events=[
            CaseEventResponse(
                id=event.id,
                event_type=event.event_type,
                created_at=event.created_at,
                actor=event.actor,
                metadata=event.event_metadata or {},
                case_id=event.case_id,
            )
            for event in events
        ],
    )

