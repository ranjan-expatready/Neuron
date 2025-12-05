"""
Document API routes for file upload and management
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.organization import Organization
from ...models.user import User
from ...schemas.document import (
    Document,
    DocumentCreate,
    DocumentUpdate,
    DocumentUploadResponse,
)
from ...services.document import DocumentService
from ..dependencies import get_current_user, get_current_user_org

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    category: Optional[str] = Form(None),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    case_id: Optional[str] = Form(None),
    person_id: Optional[str] = Form(None),
    access_level: str = Form("case_team"),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Upload a new document"""
    try:
        # Create document data
        document_data = DocumentCreate(
            document_type=document_type,
            category=category,
            title=title,
            description=description,
            access_level=access_level,
            case_id=uuid.UUID(case_id) if case_id else None,
            person_id=uuid.UUID(person_id) if person_id else None,
        )

        # Create and save document
        document = DocumentService.create_document(
            db=db,
            file=file,
            document_data=document_data,
            org_id=str(current_org.id),
            uploaded_by=str(current_user.id),
            case_id=str(case_id) if case_id else None,
            person_id=str(person_id) if person_id else None,
        )

        # Trigger OCR processing asynchronously (in production, use background tasks)
        try:
            # Process with OCR in background (non-blocking)
            DocumentService.process_document_with_ocr(
                db=db, document_id=document.id, org_id=str(current_org.id)
            )
        except Exception as e:
            # Log error but don't fail the upload
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"OCR processing failed for document {document.id}: {str(e)}")

        return DocumentUploadResponse(document=document, message="Document uploaded successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}",
        )


@router.get("/", response_model=list[Document])
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    case_id: Optional[uuid.UUID] = Query(None),
    person_id: Optional[uuid.UUID] = Query(None),
    document_type: Optional[str] = Query(None),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Get documents with filtering"""
    if case_id:
        documents = DocumentService.get_documents_by_case(
            db, str(current_org.id), str(case_id), skip, limit
        )
    elif person_id:
        documents = DocumentService.get_documents_by_person(
            db, str(current_org.id), str(person_id), skip, limit
        )
    else:
        # Get all documents for organization (you might want to add this method)
        documents = []

    # Filter by document type if provided
    if document_type:
        documents = [d for d in documents if d.document_type == document_type]

    return documents


@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Get a specific document"""
    document = DocumentService.get_document_by_id(db, str(document_id), str(current_org.id))
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.put("/{document_id}", response_model=Document)
async def update_document(
    document_id: uuid.UUID,
    document_data: DocumentUpdate,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Update document metadata"""
    update_dict = document_data.model_dump(exclude_unset=True)
    document = DocumentService.update_document(
        db, str(document_id), str(current_org.id), update_dict
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Delete a document (soft delete)"""
    success = DocumentService.delete_document(db, str(document_id), str(current_org.id))
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {"message": "Document deleted successfully"}


@router.get("/case/{case_id}", response_model=list[Document])
async def get_case_documents(
    case_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Get all documents for a specific case"""
    documents = DocumentService.get_documents_by_case(
        db, str(current_org.id), str(case_id), skip, limit
    )
    return documents


@router.get("/person/{person_id}", response_model=list[Document])
async def get_person_documents(
    person_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Get all documents for a specific person"""
    documents = DocumentService.get_documents_by_person(
        db, str(current_org.id), str(person_id), skip, limit
    )
    return documents


@router.post("/{document_id}/process-ocr")
async def process_document_ocr(
    document_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Trigger OCR processing for a document"""
    document = DocumentService.process_document_with_ocr(db, str(document_id), str(current_org.id))
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {
        "message": "OCR processing completed",
        "document": document,
        "ocr_status": document.ocr_status,
        "processing_status": document.processing_status,
    }
