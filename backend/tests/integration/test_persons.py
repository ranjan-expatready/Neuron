"""
Test suite for Person service and API
"""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.app.main import app
from src.app.models.organization import Organization, OrganizationMembership
from src.app.models.person import Person
from src.app.models.user import User
from src.app.services.auth import AuthService
from src.app.services.person import PersonService

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
        encrypted_password=AuthService.get_password_hash("testpassword123"),
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
def auth_token(test_user: User) -> str:
    """Get authentication token"""
    token = AuthService.create_access_token({"sub": test_user.email, "user_id": test_user.id})
    return token


class TestPersonService:
    """Test PersonService methods"""

    def test_create_person(self, db: Session, test_org: Organization):
        """Test person creation"""
        from src.app.schemas.person import PersonCreate

        person_data = PersonCreate(first_name="John", last_name="Doe", email="john@example.com")

        person = PersonService.create_person(db, person_data, str(test_org.id))

        assert person is not None
        assert person.org_id == test_org.id
        assert person.first_name == "John"
        assert person.last_name == "Doe"
        assert person.email == "john@example.com"

    def test_get_person_by_id(self, db: Session, test_org: Organization):
        """Test getting person by ID"""
        person = Person(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
        )
        db.add(person)
        db.commit()

        result = PersonService.get_person_by_id(db, person.id, str(test_org.id))
        assert result is not None
        assert result.id == person.id

    def test_get_person_by_id_not_found(self, db: Session, test_org: Organization):
        """Test getting non-existent person"""
        result = PersonService.get_person_by_id(db, str(uuid.uuid4()), str(test_org.id))
        assert result is None

    def test_get_persons_by_org(self, db: Session, test_org: Organization):
        """Test getting persons by organization"""
        # Create multiple persons
        for i in range(3):
            person = Person(
                id=str(uuid.uuid4()),
                org_id=test_org.id,
                first_name=f"Person{i}",
                last_name="Test",
                email=f"person{i}@example.com",
            )
            db.add(person)
        db.commit()

        persons = PersonService.get_persons_by_org(db, str(test_org.id))
        assert len(persons) >= 3

    def test_update_person(self, db: Session, test_org: Organization):
        """Test person update"""
        person = Person(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            first_name="Original",
            last_name="Name",
            email="original@example.com",
        )
        db.add(person)
        db.commit()

        from src.app.schemas.person import PersonUpdate

        update_data = PersonUpdate(first_name="Updated", email="updated@example.com")

        updated = PersonService.update_person(db, person.id, str(test_org.id), update_data)

        assert updated is not None
        assert updated.first_name == "Updated"
        assert updated.email == "updated@example.com"

    def test_delete_person(self, db: Session, test_org: Organization):
        """Test person soft delete"""
        person = Person(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            first_name="ToDelete",
            last_name="Person",
            email="delete@example.com",
        )
        db.add(person)
        db.commit()

        success = PersonService.delete_person(db, person.id, str(test_org.id))
        assert success is True

        # Verify soft delete
        deleted_person = db.query(Person).filter(Person.id == person.id).first()
        assert deleted_person.deleted_at is not None

    def test_multi_tenant_isolation(self, db: Session, test_org: Organization):
        """Test multi-tenant person isolation"""
        # Create another organization
        other_org = Organization(
            id=str(uuid.uuid4()), name="Other Organization", email="other@org.com"
        )
        db.add(other_org)
        db.commit()

        # Create person in test_org
        person = Person(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            first_name="Isolated",
            last_name="Person",
            email="isolated@example.com",
        )
        db.add(person)
        db.commit()

        # Try to access from other org (should fail)
        result = PersonService.get_person_by_id(db, person.id, str(other_org.id))
        assert result is None


class TestPersonAPI:
    """Test Person API endpoints"""

    def test_create_person_endpoint(self, client, test_org, auth_token):
        """Test POST /api/v1/persons/"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        data = {"first_name": "API", "last_name": "Test", "email": "api@example.com"}

        response = client.post("/api/v1/persons/", json=data, headers=headers)

        assert response.status_code == 200
        result = response.json()
        assert result["first_name"] == "API"
        assert result["last_name"] == "Test"

    def test_get_persons_endpoint(self, client, test_org, auth_token):
        """Test GET /api/v1/persons/"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        response = client.get("/api/v1/persons/", headers=headers)

        assert response.status_code == 200
        persons = response.json()
        assert isinstance(persons, list)

    def test_get_person_by_id_endpoint(self, client, test_org, auth_token):
        """Test GET /api/v1/persons/{person_id}"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # First create a person
        create_data = {"first_name": "Get", "last_name": "Test", "email": "get@example.com"}
        create_response = client.post("/api/v1/persons/", json=create_data, headers=headers)
        person_id = create_response.json()["id"]

        # Then get it
        response = client.get(f"/api/v1/persons/{person_id}", headers=headers)

        assert response.status_code == 200
        result = response.json()
        assert result["id"] == person_id

    def test_update_person_endpoint(self, client, test_org, auth_token):
        """Test PUT /api/v1/persons/{person_id}"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Create person
        create_data = {"first_name": "Update", "last_name": "Test", "email": "update@example.com"}
        create_response = client.post("/api/v1/persons/", json=create_data, headers=headers)
        person_id = create_response.json()["id"]

        # Update it
        update_data = {"first_name": "Updated", "email": "updated@example.com"}
        response = client.put(f"/api/v1/persons/{person_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        result = response.json()
        assert result["first_name"] == "Updated"
        assert result["email"] == "updated@example.com"

    def test_delete_person_endpoint(self, client, test_org, auth_token):
        """Test DELETE /api/v1/persons/{person_id}"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Create person
        create_data = {"first_name": "Delete", "last_name": "Test", "email": "delete@example.com"}
        create_response = client.post("/api/v1/persons/", json=create_data, headers=headers)
        person_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/api/v1/persons/{person_id}", headers=headers)

        assert response.status_code == 200
        assert response.json()["message"] == "Person deleted successfully"

        # Verify soft delete
        get_response = client.get(f"/api/v1/persons/{person_id}", headers=headers)
        assert get_response.status_code == 404
