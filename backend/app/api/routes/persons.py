from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ...db.database import get_db
from ...schemas.person import Person, PersonCreate, PersonUpdate
from ...services.person import PersonService
from ...models.user import User
from ...models.organization import Organization
from ..dependencies import get_current_user, get_current_user_org

router = APIRouter()


@router.post("/", response_model=Person)
async def create_person(
    person_data: PersonCreate,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db)
):
    """Create a new person"""
    person = PersonService.create_person(db, person_data, current_org.id)
    return person


@router.get("/", response_model=List[Person])
async def get_persons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db)
):
    """Get persons for the current organization"""
    if search:
        persons = PersonService.search_persons(db, current_org.id, search, skip, limit)
    else:
        persons = PersonService.get_persons_by_org(db, current_org.id, skip, limit)
    return persons


@router.get("/{person_id}", response_model=Person)
async def get_person(
    person_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db)
):
    """Get a specific person"""
    person = PersonService.get_person_by_id(db, person_id, current_org.id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    return person


@router.put("/{person_id}", response_model=Person)
async def update_person(
    person_id: uuid.UUID,
    person_data: PersonUpdate,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db)
):
    """Update a person"""
    person = PersonService.update_person(db, person_id, current_org.id, person_data)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    return person


@router.delete("/{person_id}")
async def delete_person(
    person_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db)
):
    """Delete a person"""
    success = PersonService.delete_person(db, person_id, current_org.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    return {"message": "Person deleted successfully"}