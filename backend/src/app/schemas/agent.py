import datetime
from typing import Any, Optional

from pydantic import BaseModel


class AgentActionResponse(BaseModel):
    id: str
    agent_name: str
    action_type: str
    status: str
    case_id: Optional[str] = None
    tenant_id: Optional[str] = None
    created_at: datetime.datetime
    payload: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class AgentSessionResponse(BaseModel):
    id: str
    agent_name: str
    status: str
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    started_at: datetime.datetime
    closed_at: Optional[datetime.datetime] = None
    created_by_user_id: Optional[str] = None
    context: Optional[dict[str, Any]] = None
    actions: list[AgentActionResponse] = []

    class Config:
        from_attributes = True

