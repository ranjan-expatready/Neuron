import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class CaseTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "normal"
    category: Optional[str] = None
    due_at: Optional[datetime] = None
    assignee_id: Optional[uuid.UUID] = None
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)
    dependencies: Optional[list[uuid.UUID]] = Field(default_factory=list)


class CaseTaskCreate(CaseTaskBase):
    case_id: uuid.UUID
    status: Optional[str] = "ready"
    source: str = "manual"


class CaseTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    due_at: Optional[datetime] = None
    assignee_id: Optional[uuid.UUID] = None
    metadata: Optional[dict[str, Any]] = None
    blocked_reason: Optional[str] = None
    dependencies: Optional[list[uuid.UUID]] = None


class CaseTaskActivityBase(BaseModel):
    activity_type: str = "comment"
    body: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class CaseTaskActivityCreate(CaseTaskActivityBase):
    pass


class CaseTaskActivity(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    author_id: Optional[uuid.UUID]
    activity_type: str
    body: Optional[str]
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    class Config:
        from_attributes = True


class CaseTask(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    case_id: uuid.UUID
    title: str
    description: Optional[str]
    status: str
    priority: str
    category: Optional[str]
    source: str
    template_item_code: Optional[str]
    assignee_id: Optional[uuid.UUID]
    due_at: Optional[datetime]
    reminder_at: Optional[datetime]
    completed_at: Optional[datetime]
    blocked_reason: Optional[str]
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    dependencies: list[uuid.UUID] = Field(default_factory=list)
    activities: Optional[list[CaseTaskActivity]] = None

    class Config:
        from_attributes = True


class CaseTaskListResponse(BaseModel):
    tasks: list[CaseTask]
    total: int
