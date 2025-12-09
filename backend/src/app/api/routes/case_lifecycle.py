from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_current_user
from src.app.cases.lifecycle_service import CaseLifecycleError, CaseLifecycleService
from src.app.cases.repository import CaseEventRepository, CaseRepository, CaseSnapshotRepository
from src.app.db.database import get_db
from src.app.models.user import User
from src.app.security.errors import TenantAccessError

router = APIRouter()


class CaseRecordResponse(BaseModel):
    id: str
    status: str
    tenant_id: str | None = None
    created_by_user_id: str | None = None
    profile: dict[str, Any] = {}
    program_eligibility: dict[str, Any] = {}


class CaseLifecycleResponse(BaseModel):
    record: CaseRecordResponse
    last_snapshot_version: int
    events: list[dict[str, Any]]


def _fetch_events(repo: CaseEventRepository, case_id: str, tenant_id: str | None) -> list[dict[str, Any]]:
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "actor": e.actor,
            "metadata": e.event_metadata or {},
            "tenant_id": e.tenant_id,
        }
        for e in repo.list_events(case_id, tenant_id=tenant_id)
    ]


def _current_snapshot_version(
    snapshot_repo: CaseSnapshotRepository, case_id: str, tenant_id: str | None
) -> int:
    snapshots = snapshot_repo.list_snapshots(case_id, tenant_id=tenant_id)
    return snapshots[-1].version if snapshots else 0


def _build_response(
    record,
    snapshot_repo: CaseSnapshotRepository,
    event_repo: CaseEventRepository,
) -> CaseLifecycleResponse:
    return CaseLifecycleResponse(
        record=CaseRecordResponse(
            id=record.id,
            status=record.status,
            tenant_id=record.tenant_id,
            created_by_user_id=record.created_by_user_id,
            profile=record.profile or {},
            program_eligibility=record.program_eligibility or {},
        ),
        last_snapshot_version=_current_snapshot_version(snapshot_repo, record.id, record.tenant_id),
        events=_fetch_events(event_repo, record.id, record.tenant_id),
    )


@router.post("/case-lifecycle/{case_id}/submit", response_model=CaseLifecycleResponse)
async def submit_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.tenant_id:
        raise TenantAccessError("Tenant context required")
    service = CaseLifecycleService(db)
    event_repo = CaseEventRepository(db)
    snapshot_repo = CaseSnapshotRepository(db)
    try:
        record = service.submit_case(case_id, current_user.id, current_user.tenant_id, current_user.role)
    except CaseLifecycleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _build_response(record, snapshot_repo, event_repo)


@router.post("/case-lifecycle/{case_id}/review", response_model=CaseLifecycleResponse)
async def mark_in_review(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.tenant_id:
        raise TenantAccessError("Tenant context required")
    service = CaseLifecycleService(db)
    event_repo = CaseEventRepository(db)
    snapshot_repo = CaseSnapshotRepository(db)
    try:
        record = service.mark_in_review(case_id, current_user.id, current_user.tenant_id, current_user.role)
    except CaseLifecycleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _build_response(record, snapshot_repo, event_repo)


@router.post("/case-lifecycle/{case_id}/complete", response_model=CaseLifecycleResponse)
async def mark_complete(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.tenant_id:
        raise TenantAccessError("Tenant context required")
    service = CaseLifecycleService(db)
    event_repo = CaseEventRepository(db)
    snapshot_repo = CaseSnapshotRepository(db)
    try:
        record = service.mark_complete(case_id, current_user.id, current_user.tenant_id, current_user.role)
    except CaseLifecycleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _build_response(record, snapshot_repo, event_repo)


@router.post("/case-lifecycle/{case_id}/archive", response_model=CaseLifecycleResponse)
async def archive_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.tenant_id:
        raise TenantAccessError("Tenant context required")
    service = CaseLifecycleService(db)
    event_repo = CaseEventRepository(db)
    snapshot_repo = CaseSnapshotRepository(db)
    try:
        record = service.archive_case(case_id, current_user.id, current_user.tenant_id, current_user.role)
    except CaseLifecycleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _build_response(record, snapshot_repo, event_repo)

