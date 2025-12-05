"""
Document service for file upload, processing, and management
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..models.document import Document
from ..schemas.document import DocumentCreate


class DocumentService:
    # Allowed file types and their MIME types
    ALLOWED_EXTENSIONS = {
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
    }

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

    # Document type mappings
    DOCUMENT_TYPE_MAPPING = {
        "passport": "identity",
        "birth_certificate": "identity",
        "diploma": "education",
        "transcript": "education",
        "ielts": "language",
        "celpip": "language",
        "tef": "language",
        "employment_letter": "work",
        "pay_stub": "work",
    }

    @staticmethod
    def get_storage_path(org_id: str, case_id: Optional[str] = None) -> str:
        """Generate storage path for document"""
        base_path = os.getenv("DOCUMENT_STORAGE_PATH", "./uploads")
        if case_id:
            return os.path.join(base_path, org_id, case_id)
        return os.path.join(base_path, org_id)

    @staticmethod
    def validate_file(file: UploadFile) -> tuple:
        """Validate uploaded file with security checks"""
        from ..middleware.security import SecurityMiddleware

        # Check file extension early to avoid unnecessary security errors
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in DocumentService.ALLOWED_EXTENSIONS:
            return (
                False,
                f"File type {file_ext} not allowed. Allowed types: {', '.join(DocumentService.ALLOWED_EXTENSIONS.keys())}",
            )

        # Determine a safe content type to pass through security validation
        allowed_content_type = DocumentService.ALLOWED_EXTENSIONS[file_ext]
        content_type = file.content_type or allowed_content_type

        # Security validation
        is_valid, error = SecurityMiddleware.validate_file_upload(
            file.filename, content_type, 0  # Size will be checked after reading
        )
        if not is_valid:
            return False, error

        # Sanitize filename
        file.filename = SecurityMiddleware.sanitize_filename(file.filename)

        return True, None

    @staticmethod
    def save_file(file: UploadFile, storage_path: str, filename: str) -> str:
        """Save uploaded file to storage"""
        os.makedirs(storage_path, exist_ok=True)
        file_path = os.path.join(storage_path, filename)

        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)

        return file_path

    @staticmethod
    def generate_storage_key(org_id: str, case_id: Optional[str], filename: str) -> str:
        """Generate unique storage key"""
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d")
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")[:50]

        if case_id:
            return f"{org_id}/{case_id}/{timestamp}/{unique_id}_{safe_filename}"
        return f"{org_id}/{timestamp}/{unique_id}_{safe_filename}"

    @staticmethod
    def get_category_from_document_type(document_type: str) -> str:
        """Get category from document type"""
        return DocumentService.DOCUMENT_TYPE_MAPPING.get(document_type.lower(), "other")

    @staticmethod
    def create_document(
        db: Session,
        file: UploadFile,
        document_data: DocumentCreate,
        org_id: str,
        uploaded_by: str,
        case_id: Optional[str] = None,
        person_id: Optional[str] = None,
    ) -> Document:
        """Create a new document record and save file"""
        # Validate file
        is_valid, error_msg = DocumentService.validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

        # Get file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > DocumentService.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {DocumentService.MAX_FILE_SIZE / (1024*1024)} MB",
            )

        # Generate storage key and path
        storage_key = DocumentService.generate_storage_key(org_id, case_id, file.filename)
        storage_path = DocumentService.get_storage_path(org_id, case_id)
        filename = f"{uuid.uuid4()}_{file.filename}"

        # Save file
        DocumentService.save_file(file, storage_path, filename)

        # Get MIME type
        file_ext = Path(file.filename).suffix.lower()
        mime_type = DocumentService.ALLOWED_EXTENSIONS.get(file_ext, "application/octet-stream")

        # Get category if not provided
        category = document_data.category or DocumentService.get_category_from_document_type(
            document_data.document_type
        )

        # Create document record
        document = Document(
            id=str(uuid.uuid4()),
            org_id=org_id,
            case_id=case_id,
            person_id=person_id,
            document_type=document_data.document_type,
            category=category,
            title=document_data.title,
            description=document_data.description,
            filename=filename,
            original_filename=file.filename,
            file_size=file_size,
            mime_type=mime_type,
            storage_key=storage_key,
            storage_provider="local",
            processing_status="pending",
            ocr_status="pending",
            validation_status="pending",
            access_level=document_data.access_level,
            tags=document_data.tags or [],
            custom_fields=document_data.custom_fields or {},
            uploaded_by=uploaded_by,
            expires_at=document_data.expires_at,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def get_document_by_id(db: Session, document_id: str, org_id: str) -> Optional[Document]:
        """Get document by ID with multi-tenant isolation"""
        return (
            db.query(Document)
            .filter(
                Document.id == document_id, Document.org_id == org_id, Document.deleted_at.is_(None)
            )
            .first()
        )

    @staticmethod
    def get_documents_by_case(
        db: Session, org_id: str, case_id: str, skip: int = 0, limit: int = 100
    ) -> list[Document]:
        """Get documents for a case"""
        return (
            db.query(Document)
            .filter(
                Document.org_id == org_id,
                Document.case_id == case_id,
                Document.deleted_at.is_(None),
            )
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_documents_by_person(
        db: Session, org_id: str, person_id: str, skip: int = 0, limit: int = 100
    ) -> list[Document]:
        """Get documents for a person"""
        return (
            db.query(Document)
            .filter(
                Document.org_id == org_id,
                Document.person_id == person_id,
                Document.deleted_at.is_(None),
            )
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_document(
        db: Session, document_id: str, org_id: str, update_data: dict
    ) -> Optional[Document]:
        """Update document metadata"""
        document = DocumentService.get_document_by_id(db, document_id, org_id)
        if not document:
            return None

        for field, value in update_data.items():
            if hasattr(document, field):
                setattr(document, field, value)

        document.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def delete_document(db: Session, document_id: str, org_id: str) -> bool:
        """Soft delete document"""
        document = DocumentService.get_document_by_id(db, document_id, org_id)
        if not document:
            return False

        document.deleted_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def update_processing_status(
        db: Session, document_id: str, org_id: str, status: str
    ) -> Optional[Document]:
        """Update document processing status"""
        document = DocumentService.get_document_by_id(db, document_id, org_id)
        if not document:
            return None

        document.processing_status = status
        if status == "completed":
            document.processed_at = datetime.utcnow()

        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def process_document_with_ocr(db: Session, document_id: str, org_id: str) -> Optional[Document]:
        """Process document with OCR to extract text and metadata"""
        document = DocumentService.get_document_by_id(db, document_id, org_id)
        if not document:
            return None

        try:
            # Update status to processing
            document.processing_status = "processing"
            document.ocr_status = "processing"
            db.commit()

            # Get full file path
            storage_path = DocumentService.get_storage_path(org_id, document.case_id)
            file_path = os.path.join(storage_path, document.filename)

            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Document file not found: {file_path}")

            # Import OCR service
            from ..services.ocr import OCRService

            # Process document with OCR
            if OCRService.is_available():
                result = OCRService.process_document(file_path, document.mime_type)

                if result["success"]:
                    # Update document with extracted data
                    document.ocr_text = result["text"]
                    document.extracted_metadata = result["metadata"]
                    document.processing_status = "completed"
                    document.ocr_status = "completed"
                    document.processed_at = datetime.utcnow()
                else:
                    document.ocr_status = "failed"
                    document.processing_status = "failed"
                    if document.validation_results is None:
                        document.validation_results = {}
                    document.validation_results["ocr_error"] = result.get(
                        "error", "Unknown OCR error"
                    )
            else:
                # OCR not available, mark as skipped
                document.ocr_status = "skipped"
                document.processing_status = "completed"
                document.processed_at = datetime.utcnow()

            db.commit()
            db.refresh(document)
            return document

        except Exception as e:
            # Update status to failed
            document.processing_status = "failed"
            document.ocr_status = "failed"
            if document.validation_results is None:
                document.validation_results = {}
            document.validation_results["processing_error"] = str(e)
            db.commit()
            db.refresh(document)
            return document
