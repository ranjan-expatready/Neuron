from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime, date
import uuid


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
    address: Optional[Dict[str, Any]] = {}
    personal_info: Optional[Dict[str, Any]] = {}
    immigration_history: Optional[Dict[str, Any]] = {}
    education: Optional[Dict[str, Any]] = {}
    work_experience: Optional[Dict[str, Any]] = {}
    language_scores: Optional[Dict[str, Any]] = {}
    family_info: Optional[Dict[str, Any]] = {}


class PersonUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nationality: Optional[str] = None
    passport_number: Optional[str] = None
    passport_expiry: Optional[date] = None
    address: Optional[Dict[str, Any]] = None
    personal_info: Optional[Dict[str, Any]] = None
    immigration_history: Optional[Dict[str, Any]] = None
    education: Optional[Dict[str, Any]] = None
    work_experience: Optional[Dict[str, Any]] = None
    language_scores: Optional[Dict[str, Any]] = None
    family_info: Optional[Dict[str, Any]] = None


class Person(PersonBase):
    id: uuid.UUID
    org_id: uuid.UUID
    address: Dict[str, Any] = {}
    personal_info: Dict[str, Any] = {}
    immigration_history: Dict[str, Any] = {}
    education: Dict[str, Any] = {}
    work_experience: Dict[str, Any] = {}
    language_scores: Dict[str, Any] = {}
    family_info: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True