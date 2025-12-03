"""
Comprehensive test suite for Document Management APIs and Services.
Target: 80%+ test coverage
"""
import os
import tempfile
import uuid
from io import BytesIO

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.app.main import app
from src.app.models.case import Case
from src.app.models.document import Document
from src.app.models.organization import Organization, OrganizationMembership
from src.app.models.person import Person
from src.app.models.user import User
from src.app.services.auth import AuthService
from src.app.services.document import DocumentService

DEFAULT_DOC_CATEGORY = "identity"
TEST_USER_PASSWORD = "testpass123"

client = TestClient(app)


@pytest.fixture
def test_org(db: Session) -> Organization:
    """Create a test organization"""
    org = Organization(id=str(uuid.uuid4()), name="Test Organization", email="test@org.com")
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def test_user(db: Session, test_org: Organization) -> User:
    """Create a test user"""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        first_name="Test",
        last_name="User",
        encrypted_password=AuthService.get_password_hash(TEST_USER_PASSWORD),
    )
    db.add(user)
    db.flush()

    membership = OrganizationMembership(
        id=str(uuid.uuid4()),
        org_id=test_org.id,
        user_id=user.id,
        role="admin",
        status="active",
    )
    db.add(membership)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_person(db: Session, test_org: Organization) -> Person:
    """Create a test person"""
    person = Person(
        id=str(uuid.uuid4()),
        org_id=test_org.id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@pytest.fixture
def test_case(db: Session, test_org: Organization, test_user: User, test_person: Person) -> Case:
    """Create a test case"""
    case = Case(
        id=str(uuid.uuid4()),
        org_id=test_org.id,
        primary_person_id=test_person.id,
        case_number="CA-20250101-TEST",
        case_type="EXPRESS_ENTRY_FSW",
        title="Test Case",
        status="draft",
        priority="normal",
        created_by=test_user.id,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@pytest.fixture
def test_file():
    """Create a test file"""
    content = b"Test PDF content"
    file = BytesIO(content)
    file.name = "test.pdf"
    return file


@pytest.fixture
def temp_storage_dir():
    """Create temporary storage directory"""
    temp_dir = tempfile.mkdtemp()
    original_path = os.getenv("DOCUMENT_STORAGE_PATH")
    os.environ["DOCUMENT_STORAGE_PATH"] = temp_dir
    yield temp_dir
    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)
    if original_path:
        os.environ["DOCUMENT_STORAGE_PATH"] = original_path
    else:
        os.environ.pop("DOCUMENT_STORAGE_PATH", None)


class TestDocumentService:
    """Test DocumentService methods"""

    def test_validate_file_valid(self, test_file):
        """Test file validation with valid file"""
        from fastapi import UploadFile

        upload_file = UploadFile(file=test_file, filename="test.pdf")
        is_valid, error = DocumentService.validate_file(upload_file)
        assert is_valid is True
        assert error is None

    def test_validate_file_invalid_extension(self):
        """Test file validation with invalid extension"""
        from fastapi import UploadFile

        file = BytesIO(b"content")
        file.name = "test.exe"
        upload_file = UploadFile(file=file, filename="test.exe")
        is_valid, error = DocumentService.validate_file(upload_file)
        assert is_valid is False
        assert "not allowed" in error

    def test_get_storage_path_with_case(self, test_org, test_case):
        """Test storage path generation with case"""
        path = DocumentService.get_storage_path(str(test_org.id), str(test_case.id))
        assert str(test_org.id) in path
        assert str(test_case.id) in path

    def test_get_storage_path_without_case(self, test_org):
        """Test storage path generation without case"""
        path = DocumentService.get_storage_path(str(test_org.id))
        assert str(test_org.id) in path

    def test_generate_storage_key(self, test_org, test_case):
        """Test storage key generation"""
        key = DocumentService.generate_storage_key(str(test_org.id), str(test_case.id), "test.pdf")
        assert str(test_org.id) in key
        assert str(test_case.id) in key
        assert "test.pdf" in key or "pdf" in key.lower()

    def test_get_category_from_document_type(self):
        """Test category mapping from document type"""
        assert DocumentService.get_category_from_document_type("passport") == "identity"
        assert DocumentService.get_category_from_document_type("diploma") == "education"
        assert DocumentService.get_category_from_document_type("ielts") == "language"
        assert DocumentService.get_category_from_document_type("unknown") == "other"

    def test_create_document(
        self,
        db: Session,
        test_org: Organization,
        test_user: User,
        test_case: Case,
        temp_storage_dir,
    ):
        """Test document creation"""
        from fastapi import UploadFile

        from src.app.schemas.document import DocumentCreate

        file_content = b"Test PDF content"
        file = BytesIO(file_content)
        file.name = "test.pdf"
        upload_file = UploadFile(file=file, filename="test.pdf")

        document_data = DocumentCreate(
            document_type="passport",
            category=DEFAULT_DOC_CATEGORY,
            title="Test Passport",
            description="Test description",
        )

        document = DocumentService.create_document(
            db=db,
            file=upload_file,
            document_data=document_data,
            org_id=str(test_org.id),
            uploaded_by=str(test_user.id),
            case_id=str(test_case.id),
        )

        assert document is not None
        assert document.org_id == test_org.id
        assert document.case_id == test_case.id
        assert document.document_type == "passport"
        assert document.title == "Test Passport"
        assert document.processing_status == "pending"

    def test_create_document_invalid_file_type(
        self, db: Session, test_org: Organization, test_user: User, temp_storage_dir
    ):
        """Test document creation with invalid file type"""
        from fastapi import UploadFile

        from src.app.schemas.document import DocumentCreate

        file = BytesIO(b"content")
        file.name = "test.exe"
        upload_file = UploadFile(file=file, filename="test.exe")

        document_data = DocumentCreate(
            document_type="passport", category=DEFAULT_DOC_CATEGORY, title="Test"
        )

        with pytest.raises(HTTPException):
            DocumentService.create_document(
                db=db,
                file=upload_file,
                document_data=document_data,
                org_id=str(test_org.id),
                uploaded_by=str(test_user.id),
            )

    def test_get_document_by_id(
        self,
        db: Session,
        test_org: Organization,
        test_user: User,
        test_case: Case,
        temp_storage_dir,
    ):
        """Test getting document by ID"""
        from fastapi import UploadFile

        from src.app.schemas.document import DocumentCreate

        # Create a document first
        file = BytesIO(b"Test content")
        file.name = "test.pdf"
        upload_file = UploadFile(file=file, filename="test.pdf")

        document_data = DocumentCreate(
            document_type="passport", category=DEFAULT_DOC_CATEGORY, title="Test Document"
        )

        created_doc = DocumentService.create_document(
            db=db,
            file=upload_file,
            document_data=document_data,
            org_id=str(test_org.id),
            uploaded_by=str(test_user.id),
            case_id=str(test_case.id),
        )

        # Get it back
        document = DocumentService.get_document_by_id(db, created_doc.id, str(test_org.id))

        assert document is not None
        assert document.id == created_doc.id

    def test_get_documents_by_case(
        self,
        db: Session,
        test_org: Organization,
        test_user: User,
        test_case: Case,
        temp_storage_dir,
    ):
        """Test getting documents by case"""
        from fastapi import UploadFile

        from src.app.schemas.document import DocumentCreate

        # Create multiple documents
        for i in range(3):
            file = BytesIO(b"Test content")
            file.name = f"test{i}.pdf"
            upload_file = UploadFile(
                file=file,
                filename=f"test{i}.pdf",
            )

            document_data = DocumentCreate(
                document_type="passport", category=DEFAULT_DOC_CATEGORY, title=f"Test Document {i}"
            )

            DocumentService.create_document(
                db=db,
                file=upload_file,
                document_data=document_data,
                org_id=str(test_org.id),
                uploaded_by=str(test_user.id),
                case_id=str(test_case.id),
            )

        documents = DocumentService.get_documents_by_case(db, str(test_org.id), str(test_case.id))

        assert len(documents) == 3

    def test_update_document(
        self,
        db: Session,
        test_org: Organization,
        test_user: User,
        test_case: Case,
        temp_storage_dir,
    ):
        """Test document update"""
        from fastapi import UploadFile

        from src.app.schemas.document import DocumentCreate

        # Create document
        file = BytesIO(b"Test content")
        file.name = "test.pdf"
        upload_file = UploadFile(file=file, filename="test.pdf")

        document_data = DocumentCreate(
            document_type="passport", category=DEFAULT_DOC_CATEGORY, title="Original Title"
        )

        document = DocumentService.create_document(
            db=db,
            file=upload_file,
            document_data=document_data,
            org_id=str(test_org.id),
            uploaded_by=str(test_user.id),
            case_id=str(test_case.id),
        )

        # Update it
        update_data = {"title": "Updated Title", "description": "Updated description"}

        updated = DocumentService.update_document(db, document.id, str(test_org.id), update_data)

        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.description == "Updated description"

    def test_delete_document(
        self,
        db: Session,
        test_org: Organization,
        test_user: User,
        test_case: Case,
        temp_storage_dir,
    ):
        """Test document soft delete"""
        from fastapi import UploadFile

        from src.app.schemas.document import DocumentCreate

        # Create document
        file = BytesIO(b"Test content")
        file.name = "test.pdf"
        upload_file = UploadFile(file=file, filename="test.pdf")

        document_data = DocumentCreate(
            document_type="passport", category=DEFAULT_DOC_CATEGORY, title="Test Document"
        )

        document = DocumentService.create_document(
            db=db,
            file=upload_file,
            document_data=document_data,
            org_id=str(test_org.id),
            uploaded_by=str(test_user.id),
            case_id=str(test_case.id),
        )

        # Delete it
        success = DocumentService.delete_document(db, document.id, str(test_org.id))
        assert success is True

        # Verify soft delete
        deleted_doc = db.query(Document).filter(Document.id == document.id).first()
        assert deleted_doc.deleted_at is not None

        # Should not be returned by get_document_by_id
        result = DocumentService.get_document_by_id(db, document.id, str(test_org.id))
        assert result is None

    def test_update_processing_status(
        self,
        db: Session,
        test_org: Organization,
        test_user: User,
        test_case: Case,
        temp_storage_dir,
    ):
        """Test processing status update"""
        from fastapi import UploadFile

        from src.app.schemas.document import DocumentCreate

        # Create document
        file = BytesIO(b"Test content")
        file.name = "test.pdf"
        upload_file = UploadFile(file=file, filename="test.pdf")

        document_data = DocumentCreate(
            document_type="passport", category=DEFAULT_DOC_CATEGORY, title="Test Document"
        )

        document = DocumentService.create_document(
            db=db,
            file=upload_file,
            document_data=document_data,
            org_id=str(test_org.id),
            uploaded_by=str(test_user.id),
            case_id=str(test_case.id),
        )

        # Update status
        updated = DocumentService.update_processing_status(
            db, document.id, str(test_org.id), "processing"
        )
        assert updated.processing_status == "processing"

        # Update to completed
        updated = DocumentService.update_processing_status(
            db, document.id, str(test_org.id), "completed"
        )
        assert updated.processing_status == "completed"
        assert updated.processed_at is not None

    def test_multi_tenant_isolation(
        self, db: Session, test_org: Organization, test_user: User, temp_storage_dir
    ):
        """Test multi-tenant document isolation"""
        from fastapi import UploadFile

        from src.app.schemas.document import DocumentCreate

        # Create another organization
        other_org = Organization(
            id=str(uuid.uuid4()), name="Other Organization", email="other@org.com"
        )
        db.add(other_org)
        db.commit()

        # Create document in test_org
        file = BytesIO(b"Test content")
        file.name = "test.pdf"
        upload_file = UploadFile(file=file, filename="test.pdf")

        document_data = DocumentCreate(
            document_type="passport", category=DEFAULT_DOC_CATEGORY, title="Test Document"
        )

        document = DocumentService.create_document(
            db=db,
            file=upload_file,
            document_data=document_data,
            org_id=str(test_org.id),
            uploaded_by=str(test_user.id),
        )

        # Try to access from other org (should fail)
        result = DocumentService.get_document_by_id(db, document.id, str(other_org.id))
        assert result is None


class TestDocumentAPI:
    """Test Document API endpoints"""

    def test_upload_document_endpoint(
        self, client, test_org, test_user, test_case, auth_token, temp_storage_dir
    ):
        """Test POST /api/v1/documents/upload"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Create multipart form data
        files = {"file": ("test.pdf", BytesIO(b"Test PDF content"), "application/pdf")}
        data = {
            "document_type": "passport",
            "category": DEFAULT_DOC_CATEGORY,
            "title": "Test Passport",
            "case_id": str(test_case.id),
        }

        response = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers)

        assert response.status_code == 200
        result = response.json()
        assert result["document"]["document_type"] == "passport"
        assert result["document"]["title"] == "Test Passport"

    def test_get_documents_endpoint(self, client, test_org, test_case, auth_token):
        """Test GET /api/v1/documents/"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        response = client.get(f"/api/v1/documents/?case_id={test_case.id}", headers=headers)

        assert response.status_code == 200
        documents = response.json()
        assert isinstance(documents, list)

    def test_get_case_documents_endpoint(self, client, test_org, test_case, auth_token):
        """Test GET /api/v1/documents/case/{case_id}"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        response = client.get(f"/api/v1/documents/case/{test_case.id}", headers=headers)

        assert response.status_code == 200
        documents = response.json()
        assert isinstance(documents, list)
