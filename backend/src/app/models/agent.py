import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Boolean
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func

from src.app.db.database import Base


class AgentSession(Base):
    __tablename__ = "agent_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=True, index=True)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="open")  # open, closed, error
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    context = Column(JSON, default={})

    def __repr__(self) -> str:
        return f"<AgentSession id={self.id} agent={self.agent_name} status={self.status}>"


class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("agent_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    tenant_id = Column(String(36), nullable=True, index=True)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    action_type = Column(String(100), nullable=False)
    payload = Column(JSON, default={})
    status = Column(String(32), nullable=False, default="suggested")  # suggested, executed, error
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    error_message = Column(String(255), nullable=True)
    auto_mode = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("ix_agent_actions_tenant_case", "tenant_id", "case_id"),
    )

    def __repr__(self) -> str:
        return f"<AgentAction id={self.id} agent={self.agent_name} type={self.action_type} status={self.status}>"

