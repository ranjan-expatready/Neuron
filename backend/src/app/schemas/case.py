import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class CaseBase(BaseModel):
    case_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    priority: str = "normal"
    target_submission_date: Optional[datetime] = None


class CaseCreate(CaseBase):
    primary_person_id: uuid.UUID
    notes: Optional[str] = None
    fee_quoted: Optional[int] = None  # in cents
    metadata: dict[str, Any] = Field(default_factory=dict)


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
    metadata: Optional[dict[str, Any]] = None
    form_data: Optional[dict[str, Any]] = None
    checklist_data: Optional[dict[str, Any]] = None
    assigned_to: Optional[uuid.UUID] = None


class Case(CaseBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    org_id: uuid.UUID
    primary_person_id: uuid.UUID
    case_number: Optional[str] = None
    status: str = "draft"
    notes: Optional[str] = None
    submitted_at: Optional[datetime] = None
    decision_date: Optional[datetime] = None
    fee_quoted: Optional[int] = None
    fee_paid: Optional[int] = None
    government_fees: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict, alias="case_metadata")
    form_data: dict[str, Any] = Field(default_factory=dict)
    checklist_data: dict[str, Any] = Field(default_factory=dict)
    eligibility_assessment: dict[str, Any] = Field(default_factory=dict)
    assigned_to: Optional[uuid.UUID] = None
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
