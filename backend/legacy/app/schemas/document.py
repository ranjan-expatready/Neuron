"""
Document schemas for API requests and responses
"""
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    document_type: str = Field(..., description="Type of document (passport, diploma, ielts, etc.)")
    category: str = Field(..., description="Category (identity, education, work, language, etc.)")
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    access_level: str = Field(default="case_team", description="Access level for the document")
    tags: list[str] = Field(default_factory=list)
    custom_fields: dict[str, Any] = Field(default_factory=dict)


class DocumentCreate(DocumentBase):
    case_id: Optional[uuid.UUID] = None
    person_id: Optional[uuid.UUID] = None
    expires_at: Optional[datetime] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    document_type: Optional[str] = None
    category: Optional[str] = None
    access_level: Optional[str] = None
    tags: Optional[list[str]] = None
    custom_fields: Optional[dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    validation_status: Optional[str] = None
    validation_notes: Optional[str] = None


class Document(DocumentBase):
    id: uuid.UUID
    org_id: uuid.UUID
    case_id: Optional[uuid.UUID] = None
    person_id: Optional[uuid.UUID] = None
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    storage_key: str
    storage_provider: str
    processing_status: str
    ocr_status: str
    validation_status: str
    ocr_text: Optional[str] = None
    extracted_metadata: dict[str, Any] = Field(default_factory=dict)
    validation_results: dict[str, Any] = Field(default_factory=dict)
    validation_notes: Optional[str] = None
    uploaded_by: uuid.UUID
    uploaded_at: datetime
    expires_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    document: Document
    message: str = "Document uploaded successfully"


class DocumentListResponse(BaseModel):
    documents: list[Document]
    total: int
    page: int
    page_size: int
