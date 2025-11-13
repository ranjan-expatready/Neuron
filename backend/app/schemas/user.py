from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


class User(UserBase):
    id: uuid.UUID
    profile: Dict[str, Any] = {}
    preferences: Dict[str, Any] = {}
    professional_info: Dict[str, Any] = {}
    last_login_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    phone_verified_at: Optional[datetime] = None
    two_factor_enabled: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True