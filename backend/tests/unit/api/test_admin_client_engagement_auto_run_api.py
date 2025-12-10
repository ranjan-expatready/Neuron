import uuid

from fastapi.testclient import TestClient

from src.app.api.dependencies import get_current_user
from src.app.models.user import User
from src.app.services.client_engagement_settings_service import ClientEngagementSettingsService
from src.app.cases.repository import CaseRepository


def _make_case(client: TestClient):
    repo = CaseRepository(client.db_session)
    case = repo.create_case(
        profile={"profile": {"personal": {"citizenship": "INDIA"}}},
        program_eligibility={"results": [{"program_code": "EE_FSW", "eligible": True}]},
        crs_breakdown=None,
        required_artifacts=None,
        config_fingerprint=None,
        source="test",
        status="evaluated",
        tenant_id=client.default_tenant.id,
        created_by="test",
        created_by_user_id=str(client.default_user.id),
    )
    client.db_session.commit()
    return case.id


def test_auto_run_tenant_scope(client: TestClient, admin_headers):
    settings = ClientEngagementSettingsService(client.db_session)
    settings.update_settings(client.default_tenant.id, auto_intake_reminders_enabled=True, auto_missing_docs_reminders_enabled=True)
    resp = client.post("/api/v1/admin/agents/client-engagement/auto-run", headers=admin_headers, json={"scope": "tenant"})
    assert resp.status_code == 200
    body = resp.json()
    assert "cases_processed" in body


def test_auto_run_case_scope(client: TestClient, admin_headers):
    settings = ClientEngagementSettingsService(client.db_session)
    settings.update_settings(client.default_tenant.id, auto_intake_reminders_enabled=True)
    case_id = _make_case(client)
    resp = client.post(
        "/api/v1/admin/agents/client-engagement/auto-run",
        headers=admin_headers,
        json={"scope": "case", "case_id": case_id},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["cases_processed"] == 1


def test_auto_run_rbac(client: TestClient):
    def _agent_user():
        return User(id=str(uuid.uuid4()), email="agent@example.com", tenant_id=str(uuid.uuid4()), role="agent")

    client.app.dependency_overrides[get_current_user] = _agent_user
    try:
        resp = client.post("/api/v1/admin/agents/client-engagement/auto-run", json={"scope": "tenant"})
        assert resp.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

