import uuid

from fastapi.testclient import TestClient

from src.app.cases.repository import CaseRepository
from src.app.api.dependencies import get_current_user
from src.app.models.user import User


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


def test_intake_reminder_endpoint(client: TestClient, admin_headers):
    case_id = _make_case(client)
    resp = client.post(
        "/api/v1/admin/agents/client-engagement/intake-reminder",
        json={"case_id": case_id},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["suggestion"]["message_type"] == "intake_incomplete_reminder"
    assert body["suggestion"]["requires_approval"] is True
    assert "llm_used" in body["suggestion"]


def test_missing_docs_endpoint(client: TestClient, admin_headers):
    case_id = _make_case(client)
    resp = client.post(
        "/api/v1/admin/agents/client-engagement/missing-docs-reminder",
        json={"case_id": case_id},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["suggestion"]["message_type"] == "missing_documents_reminder"
    assert "llm_used" in body["suggestion"]


def test_client_question_endpoint(client: TestClient, admin_headers):
    case_id = _make_case(client)
    resp = client.post(
        "/api/v1/admin/agents/client-engagement/client-question-reply",
        json={"case_id": case_id, "question_text": "What is next?"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["suggestion"]["message_type"] == "client_question_reply"
    assert "What is next?" in body["suggestion"]["body"]
    assert body["suggestion"]["requires_approval"] is True
    assert "llm_used" in body["suggestion"]


def test_client_engagement_endpoints_require_rbac(client: TestClient):
    def _agent_user():
        return User(id=str(uuid.uuid4()), email="agent@example.com", tenant_id=str(uuid.uuid4()), role="agent")

    client.app.dependency_overrides[get_current_user] = _agent_user
    try:
        resp = client.post("/api/v1/admin/agents/client-engagement/intake-reminder", json={"case_id": str(uuid.uuid4())})
        assert resp.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

