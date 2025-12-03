"""
Document model for file uploads and management
"""
import uuid

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_id = Column(
        String(36), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True
    )
    person_id = Column(
        String(36), ForeignKey("persons.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Document identification
    document_type = Column(String(100), nullable=False)  # passport, diploma, ielts, etc.
    category = Column(String(50), nullable=False)  # identity, education, work, language, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # in bytes
    mime_type = Column(String(100), nullable=False)
    storage_key = Column(String(500), nullable=False)  # S3 key or local path
    storage_provider = Column(String(50), default="local")  # local, s3, etc.

    # Processing information
    processing_status = Column(
        String(50), default="pending"
    )  # pending, processing, completed, failed
    ocr_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    validation_status = Column(
        String(50), default="pending"
    )  # pending, valid, invalid, needs_review

    # Security and access
    encryption_key_id = Column(String(255), nullable=True)
    access_level = Column(
        String(50), default="case_team"
    )  # public, case_team, consultant_only, admin_only

    # Extracted metadata
    ocr_text = Column(Text)  # Extracted text from OCR
    extracted_metadata = Column(JSON, default={})  # Extracted fields like dates, names, etc.
    tags = Column(JSON, default=[])  # Tags for categorization
    custom_fields = Column(JSON, default={})  # Custom metadata

    # Validation results
    validation_results = Column(JSON, default={})  # Validation errors/warnings
    validation_notes = Column(Text)  # Human-readable validation notes

    # Timestamps
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="documents")
    case = relationship("Case", back_populates="documents")
    person = relationship("Person", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, type={self.document_type}, status={self.processing_status})>"
