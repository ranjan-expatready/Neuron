from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class TenantCreate(BaseModel):
    name: str
    metadata: dict | None = None


class Tenant(BaseModel):
    id: str
    name: str
    metadata: dict | None = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    hashed_password: str = Field(min_length=6)
    tenant_id: str
    role: str = "agent"


class User(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    tenant_id: Optional[str] = None
    role: str

    class Config:
        from_attributes = True

