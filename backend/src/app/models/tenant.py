import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.app.db.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    plan_code = Column(String(64), nullable=False, server_default="starter")
    tenant_metadata = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    cases = relationship("CaseRecord", back_populates="tenant")

    def __repr__(self) -> str:
        return f"<Tenant id={self.id} name={self.name} plan={self.plan_code}>"

