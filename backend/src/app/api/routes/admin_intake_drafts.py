from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_current_user, get_db
from src.app.models.user import User
from src.app.schemas.intake_config_draft import (
    IntakeConfigDraftCreate,
    IntakeConfigDraftResponse,
    IntakeConfigDraftUpdate,
)
from src.app.security.errors import ForbiddenError, TenantAccessError
from src.app.services.intake_config_draft_service import IntakeConfigDraftService

router = APIRouter()


def _require_admin_or_rcic(user: User):
    if not user.tenant_id:
        raise TenantAccessError("Tenant context required")
    if user.role not in ("admin", "owner", "rcic", "rcic_admin"):
        raise ForbiddenError("Draft intake config requires admin/RCIC role")


def _require_admin_only(user: User):
    if not user.tenant_id:
        raise TenantAccessError("Tenant context required")
    if user.role not in ("admin", "owner"):
        raise ForbiddenError("Action requires admin/owner role")


@router.get("/drafts", response_model=List[IntakeConfigDraftResponse])
async def list_drafts(
    config_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin_or_rcic(current_user)
    service = IntakeConfigDraftService(db)
    return service.list_drafts(config_type=config_type, status=status)


@router.get("/drafts/{draft_id}", response_model=IntakeConfigDraftResponse)
async def get_draft(
    draft_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin_or_rcic(current_user)
    service = IntakeConfigDraftService(db)
    draft = service.get(draft_id)
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")
    return draft


@router.post("/drafts", response_model=IntakeConfigDraftResponse, status_code=status.HTTP_201_CREATED)
async def create_draft(
    payload: IntakeConfigDraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin_or_rcic(current_user)
    service = IntakeConfigDraftService(db)
    try:
        return service.create(payload, user_id=str(current_user.id))
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err


@router.patch("/drafts/{draft_id}", response_model=IntakeConfigDraftResponse)
async def update_draft(
    draft_id: str,
    payload: IntakeConfigDraftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin_or_rcic(current_user)
    service = IntakeConfigDraftService(db)
    try:
        return service.update(draft_id, payload, user_id=str(current_user.id))
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err


@router.delete("/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin_or_rcic(current_user)
    service = IntakeConfigDraftService(db)
    service.delete(draft_id, user_id=str(current_user.id))
    return {}


@router.post("/drafts/{draft_id}/submit", response_model=IntakeConfigDraftResponse)
async def submit_draft(
    draft_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # RCIC/admin can submit for review
    _require_admin_or_rcic(current_user)
    service = IntakeConfigDraftService(db)
    try:
        return service.submit(draft_id, user_id=str(current_user.id))
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err


@router.post("/drafts/{draft_id}/reject", response_model=IntakeConfigDraftResponse)
async def reject_draft(
    draft_id: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin_only(current_user)
    service = IntakeConfigDraftService(db)
    try:
        return service.reject(draft_id, user_id=str(current_user.id), notes=notes)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err


@router.post("/drafts/{draft_id}/activate", response_model=IntakeConfigDraftResponse)
async def activate_draft(
    draft_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin_only(current_user)
    service = IntakeConfigDraftService(db)
    try:
        return service.activate(draft_id, user_id=str(current_user.id))
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err


@router.post("/drafts/{draft_id}/retire", response_model=IntakeConfigDraftResponse)
async def retire_draft(
    draft_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin_only(current_user)
    service = IntakeConfigDraftService(db)
    try:
        return service.retire(draft_id, user_id=str(current_user.id))
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err

