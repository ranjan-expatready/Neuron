from fastapi.testclient import TestClient

from src.app.api.dependencies import get_current_user
from src.app.models.user import User
from src.app.services.intake_engine import clear_intake_config_cache


def test_fields_endpoint(client: TestClient, admin_headers):
    clear_intake_config_cache()
    resp = client.get("/api/v1/admin/intake/fields", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(f["id"] == "person.marital_status" for f in data)


def test_templates_endpoint_resolved(client: TestClient, admin_headers):
    clear_intake_config_cache()
    resp = client.get("/api/v1/admin/intake/templates", params={"resolved": "true"}, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    tpl = data[0]
    assert "steps" in tpl and isinstance(tpl["steps"], list)
    assert tpl["steps"][0]["fields"]  # resolved fields present


def test_documents_endpoint(client: TestClient, admin_headers):
    clear_intake_config_cache()
    resp = client.get("/api/v1/admin/intake/documents", headers=admin_headers)
    assert resp.status_code == 200
    docs = resp.json()
    assert any(doc["id"] for doc in docs)


def test_forms_endpoint(client: TestClient, admin_headers):
    clear_intake_config_cache()
    resp = client.get("/api/v1/admin/intake/forms", headers=admin_headers)
    assert resp.status_code == 200
    forms = resp.json()
    assert isinstance(forms, list)


def test_options_endpoint(client: TestClient, admin_headers):
    resp = client.get("/api/v1/admin/intake/options", headers=admin_headers)
    assert resp.status_code == 200
    opts = resp.json()
    assert "marital_status" in opts
    resp_single = client.get("/api/v1/admin/intake/options", params={"name": "education_levels"}, headers=admin_headers)
    assert resp_single.status_code == 200
    assert "education_levels" in resp_single.json()


def test_admin_intake_requires_auth(client: TestClient):
    # Override dependency to simulate non-admin/rcic user
    def _agent_user():
        return User(id="u1", email="agent@example.com", tenant_id="t1", role="agent")

    client.app.dependency_overrides[get_current_user] = _agent_user
    try:
        resp = client.get("/api/v1/admin/intake/fields")
        assert resp.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

