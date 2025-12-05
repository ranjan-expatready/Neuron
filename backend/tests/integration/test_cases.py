"""
Comprehensive test suite for Case Management APIs and Services.
Target: 80%+ test coverage
"""
import uuid

import pytest
from sqlalchemy.orm import Session

from src.app.models.case import Case
from src.app.models.organization import Organization, OrganizationMembership
from src.app.models.person import Person
from src.app.models.user import User
from src.app.services.auth import AuthService
from src.app.services.case import CaseService

TEST_USER_PASSWORD = "testpassword123"


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
def case_auth_headers(client, test_user: User) -> dict:
    """Obtain auth headers for the test user via real login flow."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


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


class TestCaseService:
    """Test CaseService methods"""

    def test_generate_case_number(self):
        """Test case number generation"""
        case_number = CaseService.generate_case_number()
        assert case_number.startswith("CA-")
        assert len(case_number) > 10

    def test_create_case(
        self, db: Session, test_org: Organization, test_user: User, test_person: Person
    ):
        """Test case creation"""
        from src.app.schemas.case import CaseCreate

        case_data = CaseCreate(
            primary_person_id=uuid.UUID(test_person.id),
            case_type="EXPRESS_ENTRY_FSW",
            title="New Test Case",
            description="Test description",
            priority="high",
        )

        case = CaseService.create_case(db, case_data, test_org.id, test_user.id)

        assert case is not None
        assert case.org_id == test_org.id
        assert case.primary_person_id == test_person.id
        assert case.case_type == "EXPRESS_ENTRY_FSW"
        assert case.status == "draft"
        assert case.priority == "high"
        assert case.case_number is not None

    def test_get_case_by_id(self, db: Session, test_org: Organization, test_case: Case):
        """Test getting case by ID"""
        case = CaseService.get_case_by_id(db, test_case.id, test_org.id)
        assert case is not None
        assert case.id == test_case.id

    def test_get_case_by_id_not_found(self, db: Session, test_org: Organization):
        """Test getting non-existent case"""
        case = CaseService.get_case_by_id(db, str(uuid.uuid4()), test_org.id)
        assert case is None

    def test_get_cases_by_org(self, db: Session, test_org: Organization, test_case: Case):
        """Test getting cases by organization"""
        cases = CaseService.get_cases_by_org(db, test_org.id)
        assert len(cases) >= 1
        assert any(c.id == test_case.id for c in cases)

    def test_update_case(self, db: Session, test_org: Organization, test_case: Case):
        """Test case update"""
        from src.app.schemas.case import CaseUpdate

        update_data = CaseUpdate(
            title="Updated Title", description="Updated description", priority="urgent"
        )

        updated_case = CaseService.update_case(db, test_case.id, test_org.id, update_data)

        assert updated_case is not None
        assert updated_case.title == "Updated Title"
        assert updated_case.description == "Updated description"
        assert updated_case.priority == "urgent"

    def test_status_transition_valid(self, db: Session, test_org: Organization, test_case: Case):
        """Test valid status transition"""
        from src.app.schemas.case import CaseUpdate

        # Transition from draft to active
        update_data = CaseUpdate(status="active")
        updated_case = CaseService.update_case(db, test_case.id, test_org.id, update_data)

        assert updated_case.status == "active"

    def test_status_transition_invalid(self, db: Session, test_org: Organization, test_case: Case):
        """Test invalid status transition"""
        from src.app.schemas.case import CaseUpdate

        # Try to transition from draft directly to approved (invalid)
        update_data = CaseUpdate(status="approved")

        with pytest.raises(ValueError, match="Cannot transition"):
            CaseService.update_case(db, test_case.id, test_org.id, update_data)

    def test_status_transition_to_submitted(
        self, db: Session, test_org: Organization, test_case: Case
    ):
        """Test status transition to submitted sets submitted_at"""
        from src.app.schemas.case import CaseUpdate

        # First transition to active
        CaseService.update_case(db, test_case.id, test_org.id, CaseUpdate(status="active"))

        # Then transition to submitted
        update_data = CaseUpdate(status="submitted")
        updated_case = CaseService.update_case(db, test_case.id, test_org.id, update_data)

        assert updated_case.status == "submitted"
        assert updated_case.submitted_at is not None

    def test_status_transition_to_approved(
        self, db: Session, test_org: Organization, test_case: Case
    ):
        """Test status transition to approved sets decision_date"""
        from src.app.schemas.case import CaseUpdate

        # Transition through valid states
        CaseService.update_case(db, test_case.id, test_org.id, CaseUpdate(status="active"))
        CaseService.update_case(db, test_case.id, test_org.id, CaseUpdate(status="submitted"))

        # Transition to approved
        update_data = CaseUpdate(status="approved")
        updated_case = CaseService.update_case(db, test_case.id, test_org.id, update_data)

        assert updated_case.status == "approved"
        assert updated_case.decision_date is not None

    def test_delete_case(self, db: Session, test_org: Organization, test_case: Case):
        """Test soft delete"""
        success = CaseService.delete_case(db, test_case.id, test_org.id)
        assert success is True

        # Case should still exist but be soft-deleted
        case = db.query(Case).filter(Case.id == test_case.id).first()
        assert case.deleted_at is not None

        # Should not be returned by get_case_by_id
        case = CaseService.get_case_by_id(db, test_case.id, test_org.id)
        assert case is None

    def test_get_cases_by_status(self, db: Session, test_org: Organization, test_case: Case):
        """Test getting cases by status"""
        cases = CaseService.get_cases_by_status(db, test_org.id, "draft")
        assert len(cases) >= 1
        assert all(c.status == "draft" for c in cases)

    def test_get_cases_by_status_invalid(self, db: Session, test_org: Organization):
        """Test getting cases with invalid status"""
        with pytest.raises(ValueError):
            CaseService.get_cases_by_status(db, test_org.id, "invalid_status")

    def test_get_cases_by_type(self, db: Session, test_org: Organization, test_case: Case):
        """Test getting cases by type"""
        cases = CaseService.get_cases_by_type(db, test_org.id, "EXPRESS_ENTRY_FSW")
        assert len(cases) >= 1
        assert all(c.case_type == "EXPRESS_ENTRY_FSW" for c in cases)

    def test_get_cases_by_person(self, db: Session, test_org: Organization, test_case: Case):
        """Test getting cases by person"""
        cases = CaseService.get_cases_by_person(db, test_org.id, test_case.primary_person_id)
        assert len(cases) >= 1
        assert any(c.id == test_case.id for c in cases)

    def test_get_case_statistics(self, db: Session, test_org: Organization, test_case: Case):
        """Test getting case statistics"""
        stats = CaseService.get_case_statistics(db, test_org.id)

        assert "total" in stats
        assert stats["total"] >= 1
        assert "draft" in stats
        assert stats["draft"] >= 1


class TestCaseAPI:
    """Test Case API endpoints"""

    def test_create_case_endpoint(
        self,
        client,
        db: Session,
        test_org: Organization,
        test_user: User,
        test_person: Person,
        case_auth_headers: dict,
    ):
        """Test POST /api/v1/cases"""
        data = {
            "primary_person_id": str(test_person.id),
            "case_type": "EXPRESS_ENTRY_FSW",
            "title": "API Test Case",
            "description": "Test description",
            "priority": "normal",
        }

        response = client.post("/api/v1/cases/", json=data, headers=case_auth_headers)

        assert response.status_code == 200
        result = response.json()
        assert result["case_type"] == "EXPRESS_ENTRY_FSW"
        assert result["title"] == "API Test Case"
        assert result["status"] == "draft"

    def test_get_cases_endpoint(
        self,
        client,
        db: Session,
        test_org: Organization,
        test_case: Case,
        case_auth_headers: dict,
    ):
        """Test GET /api/v1/cases"""

        response = client.get("/api/v1/cases/", headers=case_auth_headers)

        assert response.status_code == 200
        cases = response.json()
        assert isinstance(cases, list)
        assert len(cases) >= 1

    def test_get_case_by_id_endpoint(
        self,
        client,
        db: Session,
        test_org: Organization,
        test_case: Case,
        case_auth_headers: dict,
    ):
        """Test GET /api/v1/cases/{case_id}"""

        response = client.get(f"/api/v1/cases/{test_case.id}", headers=case_auth_headers)

        assert response.status_code == 200
        result = response.json()
        assert result["id"] == test_case.id

    def test_update_case_endpoint(
        self,
        client,
        db: Session,
        test_org: Organization,
        test_case: Case,
        case_auth_headers: dict,
    ):
        """Test PUT /api/v1/cases/{case_id}"""
        data = {"title": "Updated via API", "priority": "high"}

        response = client.put(f"/api/v1/cases/{test_case.id}", json=data, headers=case_auth_headers)

        assert response.status_code == 200
        result = response.json()
        assert result["title"] == "Updated via API"
        assert result["priority"] == "high"

    def test_update_case_status_transition(
        self,
        client,
        db: Session,
        test_org: Organization,
        test_case: Case,
        case_auth_headers: dict,
    ):
        """Test status transition via API"""

        # Transition to active
        response = client.put(
            f"/api/v1/cases/{test_case.id}", json={"status": "active"}, headers=case_auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "active"

    def test_update_case_invalid_status_transition(
        self,
        client,
        db: Session,
        test_org: Organization,
        test_case: Case,
        case_auth_headers: dict,
    ):
        """Test invalid status transition via API"""

        # Try invalid transition
        response = client.put(
            f"/api/v1/cases/{test_case.id}", json={"status": "approved"}, headers=case_auth_headers
        )
        assert response.status_code == 400

    def test_delete_case_endpoint(
        self,
        client,
        db: Session,
        test_org: Organization,
        test_case: Case,
        case_auth_headers: dict,
    ):
        """Test DELETE /api/v1/cases/{case_id}"""

        response = client.delete(f"/api/v1/cases/{test_case.id}", headers=case_auth_headers)

        assert response.status_code == 200
        assert response.json()["message"] == "Case deleted successfully"

        # Verify case is soft-deleted
        response = client.get(f"/api/v1/cases/{test_case.id}", headers=case_auth_headers)
        assert response.status_code == 404

    def test_get_cases_by_status_filter(
        self,
        client,
        db: Session,
        test_org: Organization,
        test_case: Case,
        case_auth_headers: dict,
    ):
        """Test GET /api/v1/cases?status=draft"""

        response = client.get("/api/v1/cases/?status=draft", headers=case_auth_headers)

        assert response.status_code == 200
        cases = response.json()
        assert all(c["status"] == "draft" for c in cases)

    def test_get_cases_by_type_filter(
        self,
        client,
        db: Session,
        test_org: Organization,
        test_case: Case,
        case_auth_headers: dict,
    ):
        """Test GET /api/v1/cases?case_type=EXPRESS_ENTRY_FSW"""

        response = client.get(
            "/api/v1/cases/?case_type=EXPRESS_ENTRY_FSW", headers=case_auth_headers
        )

        assert response.status_code == 200
        cases = response.json()
        assert all(c["case_type"] == "EXPRESS_ENTRY_FSW" for c in cases)

    def test_get_case_statistics_endpoint(
        self,
        client,
        db: Session,
        test_org: Organization,
        test_case: Case,
        case_auth_headers: dict,
    ):
        """Test GET /api/v1/cases/stats/summary"""

        response = client.get("/api/v1/cases/stats/summary", headers=case_auth_headers)

        assert response.status_code == 200
        stats = response.json()
        assert "total" in stats
        assert "draft" in stats

    def test_multi_tenant_isolation(
        self,
        client,
        db: Session,
        test_org: Organization,
        test_case: Case,
        case_auth_headers: dict,
    ):
        """Ensure cases from other orgs are not accessible."""
        other_org = Organization(
            id=str(uuid.uuid4()),
            name="Other Organization",
            email="other@org.com",
        )
        db.add(other_org)
        db.commit()

        other_case = Case(
            id=str(uuid.uuid4()),
            org_id=other_org.id,
            primary_person_id=test_case.primary_person_id,
            case_number="CA-OTHER-TEST",
            case_type="EXPRESS_ENTRY_FSW",
            title="Other Org Case",
            status="draft",
            priority="normal",
            created_by=test_case.created_by,
        )
        db.add(other_case)
        db.commit()

        response = client.get(f"/api/v1/cases/{other_case.id}", headers=case_auth_headers)
        assert response.status_code == 404
