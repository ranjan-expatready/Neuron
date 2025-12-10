from src.app.agents.client_engagement_agent import ClientEngagementAgent
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


def test_client_engagement_agent_logs_suggestion(client):
    case_id = _make_case(client)
    orchestrator = AgentOrchestratorService(client.db_session)
    agent = ClientEngagementAgent(orchestrator)

    result = agent.suggest_intake_reminder(case_id, tenant_id=client.default_tenant.id)
    assert "suggestion" in result

    actions = orchestrator.fetch_actions(case_id=case_id, tenant_id=client.default_tenant.id)
    assert len(actions) == 1
    assert actions[0].status == "suggested"
    assert actions[0].action_type == "suggest_intake_reminder"

    agent.suggest_missing_docs_reminder(case_id, tenant_id=client.default_tenant.id)
    agent.suggest_reply_to_client_question(case_id, question_id="q1", tenant_id=client.default_tenant.id)
    actions_all = orchestrator.fetch_actions(case_id=case_id, tenant_id=client.default_tenant.id)
    assert any(a.action_type == "suggest_missing_docs_reminder" for a in actions_all)
    assert any(a.action_type == "suggest_reply_to_client_question" for a in actions_all)

