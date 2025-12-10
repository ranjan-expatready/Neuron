from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_current_user, get_current_user_org
from src.app.cases.repository import CaseRepository
from src.app.db.database import get_db
from src.app.models.user import User
from src.app.security.errors import TenantAccessError
from src.app.services.profile_mapping import deep_merge


router = APIRouter()


class CaseProfileResponse(BaseModel):
    profile: Dict[str, Any] = Field(default_factory=dict)


class CaseProfileUpdateRequest(BaseModel):
    profile: Dict[str, Any] = Field(default_factory=dict)


def _get_case_or_404(repo: CaseRepository, case_id: str, tenant_id: Optional[str]) -> Dict[str, Any]:
    record = repo.get_case(case_id, tenant_id=tenant_id, include_deleted=False)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return record


@router.get("/cases/{case_id}/profile", response_model=CaseProfileResponse)
async def get_case_profile(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.tenant_id:
        raise TenantAccessError("Tenant context required")
    repo = CaseRepository(db)
    record = _get_case_or_404(repo, case_id, tenant_id=current_user.tenant_id)
    stored = record.profile or {}
    normalized = stored.get("profile", stored)
    return CaseProfileResponse(profile=normalized)


@router.patch("/cases/{case_id}/profile", response_model=CaseProfileResponse)
async def update_case_profile(
    case_id: str,
    payload: CaseProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.tenant_id:
        raise TenantAccessError("Tenant context required")
    repo = CaseRepository(db)
    record = _get_case_or_404(repo, case_id, tenant_id=current_user.tenant_id)
    existing = record.profile or {}
    base = existing.get("profile", existing)
    merged = deep_merge(base, payload.profile or {})
    record.profile = merged
    db.commit()
    db.refresh(record)
    return CaseProfileResponse(profile=record.profile or {})

