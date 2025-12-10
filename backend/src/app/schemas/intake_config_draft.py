from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


ConfigType = Literal["field", "template", "document", "form"]
DraftStatus = Literal["draft", "in_review", "rejected"]


class IntakeConfigDraftBase(BaseModel):
    config_type: ConfigType
    key: str = Field(..., description="Identifier for the config entry (e.g., field id, template id)")
    payload: dict[str, Any] = Field(default_factory=dict)
    status: DraftStatus = "draft"
    notes: Optional[str] = None


class IntakeConfigDraftCreate(IntakeConfigDraftBase):
    status: DraftStatus = "draft"


class IntakeConfigDraftUpdate(BaseModel):
    key: Optional[str] = None
    payload: Optional[dict[str, Any]] = None
    status: Optional[DraftStatus] = None
    notes: Optional[str] = None


class IntakeConfigDraftResponse(IntakeConfigDraftBase):
    id: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

