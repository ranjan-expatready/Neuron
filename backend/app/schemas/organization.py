from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class OrganizationBase(BaseModel):
    name: str
    domain: Optional[str] = None
    type: str = 'law_firm'


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    type: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    branding: Optional[Dict[str, Any]] = None


class Organization(OrganizationBase):
    id: uuid.UUID
    settings: Dict[str, Any] = {}
    subscription_tier: str = 'starter'
    subscription_status: str = 'active'
    billing_info: Dict[str, Any] = {}
    branding: Dict[str, Any] = {}
    compliance_settings: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrganizationMembershipBase(BaseModel):
    role: str
    status: str = 'active'


class OrganizationMembership(OrganizationMembershipBase):
    id: uuid.UUID
    org_id: uuid.UUID
    user_id: uuid.UUID
    permissions: Dict[str, Any] = {}
    invited_at: Optional[datetime] = None
    joined_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True