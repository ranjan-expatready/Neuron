"""
Test configuration and fixtures for the Canada Immigration OS backend.
"""
import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.db.database import Base, get_db
from src.app.main import app
from src.app.models import task as task_models  # noqa: F401
from src.app.models.organization import Organization, OrganizationMembership
from src.app.models.user import User
from src.app.models.tenant import Tenant  # noqa: F401
from src.app.cases.models_db import CaseRecord, CaseSnapshot, CaseEvent  # noqa: F401
from src.app.services.auth import AuthService

# Test database URL - using SQLite in memory for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def test_user(db_session, test_user_data):
    """Create a test user in the database."""
    user = User(
        email=test_user_data["email"],
        encrypted_password=AuthService.get_password_hash(test_user_data["password"]),
        first_name=test_user_data["first_name"],
        last_name=test_user_data["last_name"],
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_organization(db_session):
    """Create a test organization."""
    org = Organization(name="Test Immigration Firm", type="law_firm", settings={})
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def test_user_with_org(db_session, test_user, test_organization):
    """Create a test user with organization membership."""
    membership = OrganizationMembership(
        user_id=test_user.id, org_id=test_organization.id, role="admin", status="active"
    )
    db_session.add(membership)
    db_session.commit()
    return test_user


@pytest.fixture
def auth_headers(client, test_user_data, test_user):
    """Get authentication headers for a test user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user_data["email"], "password": test_user_data["password"]},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_token(auth_headers):
    """Raw bearer token string derived from auth_headers."""
    return auth_headers["Authorization"].split(" ", 1)[1]


@pytest.fixture
def admin_headers(client, test_user_with_org, test_user_data):
    """Get authentication headers for an admin user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user_data["email"], "password": test_user_data["password"]},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def db(db_session):
    """Backward compatible fixture name."""
    return db_session
