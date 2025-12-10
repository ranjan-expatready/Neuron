import uuid

from fastapi.testclient import TestClient

from src.app.api.dependencies import get_current_user
from src.app.models.user import User


def test_get_settings_defaults(client: TestClient, admin_headers):
    resp = client.get("/api/v1/admin/agents/client-engagement/settings", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["auto_intake_reminders_enabled"] is False
    assert body["min_days_between_intake_reminders"] == 7


def test_patch_settings_updates(client: TestClient, admin_headers):
    resp = client.patch(
        "/api/v1/admin/agents/client-engagement/settings",
        headers=admin_headers,
        json={"auto_intake_reminders_enabled": True, "min_days_between_intake_reminders": 5},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["auto_intake_reminders_enabled"] is True
    assert body["min_days_between_intake_reminders"] == 5


def test_settings_rbac_forbidden_for_agent_role(client: TestClient):
    def _agent_user():
        return User(id=str(uuid.uuid4()), email="agent@example.com", tenant_id=str(uuid.uuid4()), role="agent")

    client.app.dependency_overrides[get_current_user] = _agent_user
    try:
        resp = client.patch("/api/v1/admin/agents/client-engagement/settings", json={"auto_intake_reminders_enabled": True})
        assert resp.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

