import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, String, Text, JSON

from src.app.db.database import Base


class IntakeConfigDraft(Base):
    __tablename__ = "intake_config_drafts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    config_type = Column(
        Enum("field", "template", "document", "form", name="intake_config_type"),
        nullable=False,
        index=True,
    )
    key = Column(String(255), nullable=False, index=True)  # e.g., field id, template id
    status = Column(
        Enum("draft", "in_review", "rejected", name="intake_config_draft_status"),
        default="draft",
        nullable=False,
        index=True,
    )
    payload = Column(JSON, nullable=False)
    created_by = Column(String(36), nullable=False)
    updated_by = Column(String(36), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    notes = Column(Text, nullable=True)

