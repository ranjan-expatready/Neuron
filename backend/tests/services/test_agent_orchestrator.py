from src.app.services.agent_orchestrator import AgentOrchestratorService
from src.app.cases.repository import CaseRepository


def _make_case(client):
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


def test_create_session_and_action(client):
    case_id = _make_case(client)
    orchestrator = AgentOrchestratorService(client.db_session)

    session = orchestrator.create_session(
        agent_name="client_engagement",
        tenant_id=client.default_tenant.id,
        case_id=case_id,
        created_by_user_id=str(client.default_user.id),
    )
    assert session.id

    action = orchestrator.record_action(
        agent_name="client_engagement",
        action_type="suggest_intake_reminder",
        payload={"message": "test"},
        tenant_id=client.default_tenant.id,
        case_id=case_id,
        session_id=session.id,
    )
    assert action.session_id == session.id

    fetched = orchestrator.fetch_actions(case_id=case_id, tenant_id=client.default_tenant.id)
    assert len(fetched) == 1
    assert fetched[0].action_type == "suggest_intake_reminder"

