from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.organization import Organization as OrgModel
from ...models.user import User
from ...schemas.organization import (
    Organization,
    OrganizationCreate,
    OrganizationMembership,
    OrganizationUpdate,
)
from ...services.auth import AuthService
from ...services.organization import OrganizationService
from ..dependencies import get_current_user, get_current_user_org

router = APIRouter()


@router.get("/me", response_model=Organization)
async def get_my_organization(current_org: OrgModel = Depends(get_current_user_org)):
    """Get current user's organization"""
    return current_org


@router.put("/me", response_model=Organization)
async def update_my_organization(
    org_data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    current_org: OrgModel = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Update current user's organization"""
    updated_org = OrganizationService.update_organization(db, current_org.id, org_data)
    if not updated_org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return updated_org


@router.get("/me/members", response_model=list[OrganizationMembership])
async def get_organization_members(
    current_org: OrgModel = Depends(get_current_user_org), db: Session = Depends(get_db)
):
    """Get organization members"""
    members = OrganizationService.get_organization_members(db, current_org.id)
    return members


@router.post("/", response_model=Organization)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new organization (for users without one)"""
    # Check if user already has an organization
    existing_org = AuthService.get_user_organization(db, current_user)
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already belongs to an organization",
        )

    org = OrganizationService.create_organization(db, org_data, current_user.id)
    return org
