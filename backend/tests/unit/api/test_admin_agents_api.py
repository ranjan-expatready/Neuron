import uuid

from fastapi.testclient import TestClient

from src.app.services.agent_orchestrator import AgentOrchestratorService
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


def test_list_agent_actions(client: TestClient, admin_headers):
    case_id = _make_case(client)
    orchestrator = AgentOrchestratorService(client.db_session)
    orchestrator.record_action(
        agent_name="client_engagement",
        action_type="suggest_intake_reminder",
        payload={"message": "test"},
        tenant_id=client.default_tenant.id,
        case_id=case_id,
    )

    resp = client.get("/api/v1/admin/agents/actions", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["agent_name"] == "client_engagement"


def test_get_agent_session(client: TestClient, admin_headers):
    case_id = _make_case(client)
    orchestrator = AgentOrchestratorService(client.db_session)
    session = orchestrator.create_session(
        agent_name="client_engagement", tenant_id=client.default_tenant.id, case_id=case_id
    )
    orchestrator.record_action(
        agent_name="client_engagement",
        action_type="suggest_missing_docs_reminder",
        payload={"message": "test"},
        tenant_id=client.default_tenant.id,
        case_id=case_id,
        session_id=session.id,
    )

    resp = client.get(f"/api/v1/admin/agents/sessions/{session.id}", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == session.id
    assert len(body["actions"]) >= 1


def test_admin_agents_requires_rbac(client: TestClient):
    def _agent_user():
        return User(id=str(uuid.uuid4()), email="agent@example.com", tenant_id=str(uuid.uuid4()), role="agent")

    client.app.dependency_overrides[get_current_user] = _agent_user
    try:
        resp = client.get("/api/v1/admin/agents/actions")
        assert resp.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

