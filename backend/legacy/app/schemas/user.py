import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr


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
    profile: Optional[dict[str, Any]] = None
    preferences: Optional[dict[str, Any]] = None


class User(UserBase):
    id: uuid.UUID
    profile: dict[str, Any] = {}
    preferences: dict[str, Any] = {}
    professional_info: dict[str, Any] = {}
    last_login_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    phone_verified_at: Optional[datetime] = None
    two_factor_enabled: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
