import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from src.app.db.database import Base


class ClientEngagementSettings(Base):
    __tablename__ = "client_engagement_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    auto_intake_reminders_enabled = Column(Boolean, nullable=False, default=False)
    auto_missing_docs_reminders_enabled = Column(Boolean, nullable=False, default=False)
    min_days_between_intake_reminders = Column(Integer, nullable=False, default=7)
    min_days_between_docs_reminders = Column(Integer, nullable=False, default=7)
    quiet_hours_start = Column(Integer, nullable=True)  # optional future use, hour of day 0-23
    quiet_hours_end = Column(Integer, nullable=True)    # optional future use, hour of day 0-23
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ClientEngagementSettings tenant_id={self.tenant_id}>"

