from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_current_user
from src.app.db.database import get_db
from src.app.models.user import User
from src.app.security.errors import ForbiddenError, TenantAccessError
from src.app.services.billing_service import BillingService

router = APIRouter()


def _require_admin(user: User) -> None:
    if not user.tenant_id:
        raise TenantAccessError("Tenant context required")
    if user.role not in ("admin", "owner"):
        raise ForbiddenError("Billing admin requires admin/owner role")


class PlanUpdateRequest(BaseModel):
    plan_code: str
    subscription_status: Optional[str] = None
    renewal_date: Optional[datetime] = None


@router.get("/state")
async def get_billing_state(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    billing_service = BillingService(db)
    return billing_service.get_plan_status(current_user.tenant_id)


@router.get("/usage")
async def get_billing_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    billing_service = BillingService(db)
    return billing_service.get_usage_snapshot(current_user.tenant_id)


@router.post("/update-plan")
async def update_plan(
    payload: PlanUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    billing_service = BillingService(db)
    try:
        return billing_service.set_plan_status(
            tenant_id=current_user.tenant_id,
            plan_code=payload.plan_code,
            subscription_status=payload.subscription_status,
            renewal_date=payload.renewal_date,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.get("/portal-url")
async def get_portal_url_stub(
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    return {"portal_url": "https://billing.example.com/tenant-portal"}

