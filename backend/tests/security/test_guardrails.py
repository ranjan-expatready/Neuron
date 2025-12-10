import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_current_user, get_current_user_org
from src.app.cases.lifecycle_service import CaseLifecycleService
from src.app.cases.repository import CaseRepository
from src.app.db.database import get_db
from src.app.models.organization import Organization, OrganizationMembership
from src.app.models.tenant import Tenant
from src.app.models.user import User
from src.app.security.errors import LifecyclePermissionError
from src.app.services.auth import AuthService


def test_auth_required_for_case_history(client: TestClient):
    """Test that unauthenticated requests return 401 or 403 (depending on middleware order)."""
    # Save original override
    original_override = client.app.dependency_overrides.get(get_current_user)

    try:
        # remove override to simulate missing auth
        client.app.dependency_overrides.pop(get_current_user, None)
        resp = client.get("/api/v1/case-history")
        # FastAPI's HTTPBearer can return 401 or 403 depending on configuration
        assert resp.status_code in (401, 403)
    finally:
        # Restore original override
        if original_override:
            client.app.dependency_overrides[get_current_user] = original_override


def test_cross_tenant_access_blocked(client: TestClient):
    """Test that users cannot access other tenant's cases."""
    db = client.app.dependency_overrides[get_db]().__next__()  # type: ignore
    tenant1 = client.default_tenant
    user1 = client.default_user

    # Save original overrides
    original_user_override = client.app.dependency_overrides.get(get_current_user)
    original_org_override = client.app.dependency_overrides.get(get_current_user_org)

    # Create second tenant/user
    tenant2 = Tenant(name="Tenant Two")
    db.add(tenant2)
    db.commit()
    db.refresh(tenant2)

    user2 = User(
        email="user2@example.com",
        encrypted_password=AuthService.get_password_hash("password123"),
        tenant_id=tenant2.id,
        role="admin",
    )
    db.add(user2)
    db.commit()
    db.refresh(user2)

    # Create org for user2
    org2 = Organization(name="Org Two", type="law_firm", settings={})
    db.add(org2)
    db.commit()
    db.refresh(org2)

    membership2 = OrganizationMembership(
        user_id=user2.id, org_id=org2.id, role="admin", status="active"
    )
    db.add(membership2)
    db.commit()

    # Create case under tenant1
    repo = CaseRepository(db)
    case = repo.create_case(
        profile={},
        program_eligibility={},
        crs_breakdown={},
        required_artifacts={},
        config_fingerprint={},
        source="test",
        tenant_id=tenant1.id,
        created_by=user1.id,
        created_by_user_id=user1.id,
    )
    db.commit()

    def override_user():
        return user2

    def override_org():
        return org2

    try:
        client.app.dependency_overrides[get_current_user] = override_user
        client.app.dependency_overrides[get_current_user_org] = override_org
        resp = client.get(f"/api/v1/case-history/{case.id}")
        # Should be 403 or 404 (case not found for this tenant)
        assert resp.status_code in (403, 404)
    finally:
        # Restore original overrides
        if original_user_override:
            client.app.dependency_overrides[get_current_user] = original_user_override
        if original_org_override:
            client.app.dependency_overrides[get_current_user_org] = original_org_override


def test_lifecycle_rbac_blocks_viewer(client: TestClient):
    """Test that viewer role cannot perform lifecycle transitions."""
    db = client.app.dependency_overrides[get_db]().__next__()  # type: ignore
    service = CaseLifecycleService(db)
    case = service.create_case(
        profile={},
        tenant_id=client.default_tenant.id,
        user_id=client.default_user.id,
        source="test",
    )
    # Test RBAC by calling submit_case with viewer role
    with pytest.raises(LifecyclePermissionError):
        service.submit_case(
            case.id, client.default_user.id, client.default_tenant.id, role="viewer"
        )


def test_soft_delete_excludes_from_history(client: TestClient):
    """Test that soft-deleted cases don't appear in history listing."""
    db = client.app.dependency_overrides[get_db]().__next__()  # type: ignore
    repo = CaseRepository(db)
    record = repo.create_case(
        profile={},
        program_eligibility={},
        crs_breakdown={},
        required_artifacts={},
        config_fingerprint={},
        source="test",
        tenant_id=client.default_tenant.id,
        created_by=client.default_user.id,
        created_by_user_id=client.default_user.id,
    )
    db.commit()
    repo.soft_delete(record.id, tenant_id=client.default_tenant.id)
    db.commit()
    resp = client.get("/api/v1/case-history")
    assert resp.status_code == 200
    assert all(item["id"] != record.id for item in resp.json())
