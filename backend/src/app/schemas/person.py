import uuid
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr


class PersonBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nationality: Optional[str] = None
    passport_number: Optional[str] = None
    passport_expiry: Optional[date] = None


class PersonCreate(PersonBase):
    address: Optional[dict[str, Any]] = {}
    personal_info: Optional[dict[str, Any]] = {}
    immigration_history: Optional[dict[str, Any]] = {}
    education: Optional[dict[str, Any]] = {}
    work_experience: Optional[dict[str, Any]] = {}
    language_scores: Optional[dict[str, Any]] = {}
    family_info: Optional[dict[str, Any]] = {}


class PersonUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nationality: Optional[str] = None
    passport_number: Optional[str] = None
    passport_expiry: Optional[date] = None
    address: Optional[dict[str, Any]] = None
    personal_info: Optional[dict[str, Any]] = None
    immigration_history: Optional[dict[str, Any]] = None
    education: Optional[dict[str, Any]] = None
    work_experience: Optional[dict[str, Any]] = None
    language_scores: Optional[dict[str, Any]] = None
    family_info: Optional[dict[str, Any]] = None


class Person(PersonBase):
    id: uuid.UUID
    org_id: uuid.UUID
    address: dict[str, Any] = {}
    personal_info: dict[str, Any] = {}
    immigration_history: dict[str, Any] = {}
    education: dict[str, Any] = {}
    work_experience: dict[str, Any] = {}
    language_scores: dict[str, Any] = {}
    family_info: dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
