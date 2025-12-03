import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.database import Base


class Person(Base):
    __tablename__ = "persons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date)
    email = Column(String(255), index=True)
    phone = Column(String(20))
    nationality = Column(String(100))
    passport_number = Column(String(50))
    passport_expiry = Column(Date)
    address = Column(JSON, default={})  # structured address data
    personal_info = Column(JSON, default={})  # additional personal details
    immigration_history = Column(JSON, default={})  # previous applications, visas, etc.
    education = Column(JSON, default={})  # education history
    work_experience = Column(JSON, default={})  # work experience
    language_scores = Column(JSON, default={})  # IELTS, CELPIP, TEF, etc.
    family_info = Column(JSON, default={})  # spouse, children, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    organization = relationship("Organization", back_populates="persons")
    primary_cases = relationship("Case", back_populates="primary_person")
    documents = relationship("Document", back_populates="person")

    def __repr__(self):
        return (
            f"<Person(id={self.id}, name={self.first_name} {self.last_name}, org_id={self.org_id})>"
        )
