from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ...db.database import get_db
from ...schemas.case import Case, CaseCreate, CaseUpdate
from ...services.case import CaseService
from ...services.person import PersonService
from ...models.user import User
from ...models.organization import Organization
from ..dependencies import get_current_user, get_current_user_org

router = APIRouter()


@router.post("/", response_model=Case)
async def create_case(
    case_data: CaseCreate,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db)
):
    """Create a new case"""
    # Verify the person belongs to the organization
    person = PersonService.get_person_by_id(db, case_data.primary_person_id, current_org.id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person not found or does not belong to your organization"
        )
    
    case = CaseService.create_case(db, case_data, current_org.id, current_user.id)
    return case


@router.get("/", response_model=List[Case])
async def get_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, alias="status"),
    case_type: Optional[str] = Query(None),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db)
):
    """Get cases for the current organization"""
    if status_filter:
        cases = CaseService.get_cases_by_status(db, current_org.id, status_filter, skip, limit)
    elif case_type:
        cases = CaseService.get_cases_by_type(db, current_org.id, case_type, skip, limit)
    else:
        cases = CaseService.get_cases_by_org(db, current_org.id, skip, limit)
    return cases


@router.get("/{case_id}", response_model=Case)
async def get_case(
    case_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db)
):
    """Get a specific case"""
    case = CaseService.get_case_by_id(db, case_id, current_org.id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    return case


@router.put("/{case_id}", response_model=Case)
async def update_case(
    case_id: uuid.UUID,
    case_data: CaseUpdate,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db)
):
    """Update a case"""
    case = CaseService.update_case(db, case_id, current_org.id, case_data)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    return case


@router.delete("/{case_id}")
async def delete_case(
    case_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db)
):
    """Delete a case"""
    success = CaseService.delete_case(db, case_id, current_org.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    return {"message": "Case deleted successfully"}


@router.get("/person/{person_id}", response_model=List[Case])
async def get_cases_by_person(
    person_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db)
):
    """Get all cases for a specific person"""
    # Verify the person belongs to the organization
    person = PersonService.get_person_by_id(db, person_id, current_org.id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    cases = CaseService.get_cases_by_person(db, current_org.id, person_id)
    return cases