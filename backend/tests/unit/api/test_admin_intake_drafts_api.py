import uuid

from fastapi.testclient import TestClient

from src.app.schemas.intake_config_draft import IntakeConfigDraftCreate


def _sample_field_draft() -> dict:
    return {
        "config_type": "field",
        "key": "person.test_field",
        "payload": {
            "id": "person.test_field",
            "label": "Test Field",
            "data_path": "profile.personal.test_field",
            "type": "string",
            "ui_control": "text",
        },
    }


def test_create_get_update_delete_draft(client: TestClient, admin_headers):
    create_resp = client.post("/api/v1/admin/intake/drafts", headers=admin_headers, json=_sample_field_draft())
    assert create_resp.status_code == 201
    created = create_resp.json()
    draft_id = created["id"]

    get_resp = client.get(f"/api/v1/admin/intake/drafts/{draft_id}", headers=admin_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["key"] == "person.test_field"

    patch_resp = client.patch(
        f"/api/v1/admin/intake/drafts/{draft_id}",
        headers=admin_headers,
        json={"notes": "updated"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["notes"] == "updated"

    del_resp = client.delete(f"/api/v1/admin/intake/drafts/{draft_id}", headers=admin_headers)
    assert del_resp.status_code == 204


def test_status_transitions(client: TestClient, admin_headers):
    create_resp = client.post("/api/v1/admin/intake/drafts", headers=admin_headers, json=_sample_field_draft())
    draft_id = create_resp.json()["id"]

    # submit draft -> in_review
    submit_resp = client.post(f"/api/v1/admin/intake/drafts/{draft_id}/submit", headers=admin_headers)
    assert submit_resp.status_code == 200
    assert submit_resp.json()["status"] == "in_review"

    # activate -> active
    activate_resp = client.post(f"/api/v1/admin/intake/drafts/{draft_id}/activate", headers=admin_headers)
    assert activate_resp.status_code == 200
    assert activate_resp.json()["status"] == "active"

    # retire -> retired
    retire_resp = client.post(f"/api/v1/admin/intake/drafts/{draft_id}/retire", headers=admin_headers)
    assert retire_resp.status_code == 200
    assert retire_resp.json()["status"] == "retired"


def test_invalid_transition(client: TestClient, admin_headers):
    create_resp = client.post("/api/v1/admin/intake/drafts", headers=admin_headers, json=_sample_field_draft())
    draft_id = create_resp.json()["id"]
    # activate directly from draft should fail
    activate_resp = client.post(f"/api/v1/admin/intake/drafts/{draft_id}/activate", headers=admin_headers)
    assert activate_resp.status_code == 400


def test_list_filtering(client: TestClient, admin_headers):
    # create two drafts
    client.post("/api/v1/admin/intake/drafts", headers=admin_headers, json=_sample_field_draft())
    client.post(
        "/api/v1/admin/intake/drafts",
        headers=admin_headers,
        json={
            "config_type": "document",
            "key": "doc.sample",
            "payload": {
                "id": "doc.sample",
                "label": "Sample Doc",
                "category": "identity",
                "required_for_programs": [],
                "required_when": [],
            },
        },
    )
    resp = client.get("/api/v1/admin/intake/drafts?config_type=document", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert all(d["config_type"] == "document" for d in data)


def test_invalid_payload_validation(client: TestClient, admin_headers):
    bad_payload = {
        "config_type": "field",
        "key": "invalid",
        "payload": {"id": "invalid"},  # missing required attributes
    }
    resp = client.post("/api/v1/admin/intake/drafts", headers=admin_headers, json=bad_payload)
    assert resp.status_code == 400


def test_requires_admin_roles(client: TestClient):
    # simulate agent user via dependency override
    from src.app.api.dependencies import get_current_user
    from src.app.models.user import User

    def _agent_user():
        return User(id=str(uuid.uuid4()), email="agent@example.com", tenant_id=str(uuid.uuid4()), role="agent")

    client.app.dependency_overrides[get_current_user] = _agent_user
    try:
        resp2 = client.get("/api/v1/admin/intake/drafts")
        assert resp2.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)


def test_admin_only_activation(client: TestClient, admin_headers):
    # create draft
    create_resp = client.post("/api/v1/admin/intake/drafts", headers=admin_headers, json=_sample_field_draft())
    draft_id = create_resp.json()["id"]
    # submit as admin for simplicity
    client.post(f"/api/v1/admin/intake/drafts/{draft_id}/submit", headers=admin_headers)

    # override current user to rcic to attempt activation (should fail)
    from src.app.api.dependencies import get_current_user
    from src.app.models.user import User

    def _rcic_user():
        return User(id=str(uuid.uuid4()), email="rcic@example.com", tenant_id=str(uuid.uuid4()), role="rcic")

    client.app.dependency_overrides[get_current_user] = _rcic_user
    try:
        resp = client.post(f"/api/v1/admin/intake/drafts/{draft_id}/activate")
        assert resp.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

