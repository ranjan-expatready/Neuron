from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class ConfigCaseTypeBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


class ConfigCaseType(ConfigCaseTypeBase):
    id: uuid.UUID
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConfigFormBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    step_number: int = 1
    is_required: bool = True
    is_active: bool = True


class ConfigForm(ConfigFormBase):
    id: uuid.UUID
    case_type_id: uuid.UUID
    form_schema: Dict[str, Any] = {}
    ui_schema: Dict[str, Any] = {}
    validation_rules: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConfigFieldBase(BaseModel):
    field_code: str
    field_name: str
    field_type: str
    form_code: str
    is_required: bool = False
    is_active: bool = True
    sort_order: int = 0


class ConfigField(ConfigFieldBase):
    id: uuid.UUID
    case_type_id: uuid.UUID
    validation_rules: Dict[str, Any] = {}
    options: Dict[str, Any] = {}
    help_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True