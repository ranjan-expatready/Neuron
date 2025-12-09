import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.organization import Organization
from ...models.user import User
from ...schemas.case import Case, CaseCreate, CaseUpdate
from ...services.case import CaseService
from ...services.billing_service import BillingService
from ...services.person import PersonService
from ...services.task import CaseTaskService
from ..dependencies import get_current_user, get_current_user_org
from ...security.errors import TenantAccessError

router = APIRouter()


@router.post("/", response_model=Case)
async def create_case(
    case_data: CaseCreate,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Create a new case"""
    if not current_user.tenant_id:
        raise TenantAccessError("Tenant context required")
    billing_service = BillingService(db)
    billing_service.apply_plan_limits(current_user.tenant_id, "case_created")
    # Verify the person belongs to the organization
    person = PersonService.get_person_by_id(db, case_data.primary_person_id, str(current_org.id))
    if not person:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person not found or does not belong to your organization",
        )

    case = CaseService.create_case(db, case_data, str(current_org.id), str(current_user.id))
    billing_service.record_usage_event(current_user.tenant_id, "case_created")
    return case


@router.get("/", response_model=list[Case])
async def get_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, alias="status"),
    case_type: Optional[str] = Query(None),
    assigned_to: Optional[uuid.UUID] = Query(None),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Get cases for the current organization with filtering"""
    try:
        if status_filter:
            cases = CaseService.get_cases_by_status(
                db, str(current_org.id), status_filter, skip, limit
            )
        elif case_type:
            cases = CaseService.get_cases_by_type(db, str(current_org.id), case_type, skip, limit)
        elif assigned_to:
            cases = CaseService.get_cases_by_assigned_user(
                db, str(current_org.id), str(assigned_to), skip, limit
            )
        else:
            cases = CaseService.get_cases_by_org(db, str(current_org.id), skip, limit)
        return cases
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err


@router.get("/{case_id}", response_model=Case)
async def get_case(
    case_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Get a specific case"""
    case = CaseService.get_case_by_id(db, str(case_id), str(current_org.id))
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.put("/{case_id}", response_model=Case)
async def update_case(
    case_id: uuid.UUID,
    case_data: CaseUpdate,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Update a case with lifecycle management"""
    try:
        case = CaseService.update_case(db, str(case_id), str(current_org.id), case_data)
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        return case
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err


@router.delete("/{case_id}")
async def delete_case(
    case_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Delete a case (soft delete)"""
    success = CaseService.delete_case(db, str(case_id), str(current_org.id))
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return {"message": "Case deleted successfully"}


@router.get("/person/{person_id}", response_model=list[Case])
async def get_cases_by_person(
    person_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Get all cases for a specific person"""
    # Verify the person belongs to the organization
    person = PersonService.get_person_by_id(db, person_id, str(current_org.id))
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    cases = CaseService.get_cases_by_person(db, str(current_org.id), str(person_id))
    return cases


@router.get("/stats/summary")
async def get_case_statistics(
    current_org: Organization = Depends(get_current_user_org), db: Session = Depends(get_db)
):
    """Get case statistics for the current organization"""
    stats = CaseService.get_case_statistics(db, str(current_org.id))
    return stats


@router.post("/{case_id}/tasks/sync")
async def sync_case_tasks(
    case_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sync case tasks with checklist template."""
    case = CaseService.get_case_by_id(db, str(case_id), str(current_org.id))
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    created = CaseTaskService.sync_case_tasks(db, case)
    return {
        "synced": created,
        "message": "Tasks synchronized" if created else "No new tasks added",
        "requested_by": str(current_user.id),
    }
