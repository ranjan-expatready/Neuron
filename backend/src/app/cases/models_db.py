import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.app.db.database import Base


class CaseRecord(Base):
    """Canonical current state for a case evaluation."""

    __tablename__ = "case_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    source = Column(String(100), nullable=False, index=True)
    status = Column(
        String(50),
        nullable=False,
        default="draft",
    )
    profile = Column(JSON, nullable=False)
    program_eligibility = Column(JSON, nullable=False)
    crs_breakdown = Column(JSON, nullable=True)
    required_artifacts = Column(JSON, nullable=True)
    config_fingerprint = Column(JSON, nullable=True)
    tenant_id = Column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    created_by_user_id = Column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by = Column(String(64), nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    tenant = relationship("Tenant", back_populates="cases")
    creator_user = relationship("User", back_populates="created_cases")

    snapshots = relationship(
        "CaseSnapshot",
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseSnapshot.version",
    )
    events = relationship(
        "CaseEvent",
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseEvent.created_at",
    )

    def __repr__(self) -> str:
        return f"<CaseRecord id={self.id} source={self.source} status={self.status}>"


class CaseSnapshot(Base):
    """Immutable snapshot for each evaluation run."""

    __tablename__ = "case_snapshots"
    __table_args__ = (
        UniqueConstraint("case_id", "version", name="uq_case_snapshots_case_version"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(
        String(36), ForeignKey("case_records.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snapshot_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source = Column(String(100), nullable=False, index=True)
    tenant_id = Column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    profile = Column(JSON, nullable=False)
    program_eligibility = Column(JSON, nullable=False)
    crs_breakdown = Column(JSON, nullable=True)
    required_artifacts = Column(JSON, nullable=True)
    config_fingerprint = Column(JSON, nullable=True)
    version = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    case = relationship("CaseRecord", back_populates="snapshots")

    def __repr__(self) -> str:
        return f"<CaseSnapshot case_id={self.case_id} version={self.version}>"


class CaseEvent(Base):
    """Audit events for case evaluations."""

    __tablename__ = "case_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(
        String(36), ForeignKey("case_records.id", ondelete="SET NULL"), nullable=True, index=True
    )
    event_type = Column(String(100), nullable=False)
    tenant_id = Column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    actor = Column(String(100), nullable=False, default="system")
    event_metadata = Column("metadata", JSON, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    case = relationship("CaseRecord", back_populates="events")

    def __repr__(self) -> str:
        return f"<CaseEvent id={self.id} event_type={self.event_type} case_id={self.case_id}>"

