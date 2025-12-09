"""
Test configuration and fixtures for the Canada Immigration OS backend.
"""
import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.api.dependencies import get_current_user, get_current_user_org
from src.app.db.database import Base, get_db
from src.app.main import app
from src.app.models import task as task_models  # noqa: F401
from src.app.models.organization import Organization, OrganizationMembership
from src.app.models.tenant import Tenant  # noqa: F401
from src.app.models.user import User
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

    # Seed a default tenant/user for auth overrides
    tenant = Tenant(name="Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    org = Organization(name="Test Org", type="law_firm", settings={})
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    user = User(
        email="test@example.com",
        encrypted_password=AuthService.get_password_hash("testpass123"),
        tenant_id=tenant.id,
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    membership = OrganizationMembership(
        user_id=user.id, org_id=org.id, role="admin", status="active"
    )
    db_session.add(membership)
    db_session.commit()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        return user

    def override_get_current_user_org():
        return org

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_user_org] = override_get_current_user_org

    with TestClient(app) as test_client:
        test_client.default_user = user
        test_client.default_tenant = tenant
        test_client.default_org = org
        test_client.db_session = db_session
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
    token = AuthService.create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_token(auth_headers):
    """Raw bearer token string derived from auth_headers."""
    return auth_headers["Authorization"].split(" ", 1)[1]


@pytest.fixture
def admin_headers(client, test_user_with_org, test_user_data):
    """Get authentication headers for an admin user."""
    token = AuthService.create_access_token(data={"sub": test_user_with_org.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def db(db_session):
    """Backward compatible fixture name."""
    return db_session
