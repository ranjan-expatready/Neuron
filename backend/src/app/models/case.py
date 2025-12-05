import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.database import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    primary_person_id = Column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False
    )
    case_number = Column(String(50), unique=True, index=True)  # internal case number
    case_type = Column(String(100), nullable=False)  # EXPRESS_ENTRY_FSW, STUDY_PERMIT, etc.
    status = Column(
        String(50), default="draft"
    )  # draft, active, submitted, approved, rejected, closed
    priority = Column(String(20), default="normal")  # low, normal, high, urgent

    # Case details
    title = Column(String(255))
    description = Column(Text)
    notes = Column(Text)

    # Dates
    target_submission_date = Column(DateTime(timezone=True))
    submitted_at = Column(DateTime(timezone=True))
    decision_date = Column(DateTime(timezone=True))

    # Financial
    fee_quoted = Column(Integer)  # in cents
    fee_paid = Column(Integer)  # in cents
    government_fees = Column(Integer)  # in cents

    # Metadata
    case_metadata = Column(JSON, default={})  # flexible storage for case-specific data
    form_data = Column(JSON, default={})  # form responses and data
    checklist_data = Column(JSON, default={})  # checklist completion status
    eligibility_assessment = Column(JSON, default={})  # eligibility results

    # Audit fields
    assigned_to = Column(String(36), ForeignKey("users.id"))
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    organization = relationship("Organization", back_populates="cases")
    primary_person = relationship("Person", back_populates="primary_cases")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])
    documents = relationship("Document", back_populates="case")

    def __repr__(self):
        return f"<Case(id={self.id}, case_number={self.case_number}, type={self.case_type}, status={self.status})>"
