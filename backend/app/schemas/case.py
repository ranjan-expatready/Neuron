from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class CaseBase(BaseModel):
    case_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    priority: str = 'normal'
    target_submission_date: Optional[datetime] = None


class CaseCreate(CaseBase):
    primary_person_id: uuid.UUID
    notes: Optional[str] = None
    fee_quoted: Optional[int] = None  # in cents
    metadata: Optional[Dict[str, Any]] = {}


class CaseUpdate(BaseModel):
    case_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    target_submission_date: Optional[datetime] = None
    fee_quoted: Optional[int] = None
    fee_paid: Optional[int] = None
    government_fees: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    form_data: Optional[Dict[str, Any]] = None
    checklist_data: Optional[Dict[str, Any]] = None
    assigned_to: Optional[uuid.UUID] = None


class Case(CaseBase):
    id: uuid.UUID
    org_id: uuid.UUID
    primary_person_id: uuid.UUID
    case_number: Optional[str] = None
    status: str = 'draft'
    notes: Optional[str] = None
    submitted_at: Optional[datetime] = None
    decision_date: Optional[datetime] = None
    fee_quoted: Optional[int] = None
    fee_paid: Optional[int] = None
    government_fees: Optional[int] = None
    metadata: Dict[str, Any] = {}
    form_data: Dict[str, Any] = {}
    checklist_data: Dict[str, Any] = {}
    eligibility_assessment: Dict[str, Any] = {}
    assigned_to: Optional[uuid.UUID] = None
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True