from src.app.agents.client_engagement_agent import ClientEngagementAgent
from src.app.services.agent_orchestrator import AgentOrchestratorService
from src.app.cases.repository import CaseRepository


def _make_case(client):
    repo = CaseRepository(client.db_session)
    case = repo.create_case(
        profile={"profile": {"personal": {"citizenship": "INDIA"}, "client_name": "Alex"}} ,
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


def _make_agent(client):
    orchestrator = AgentOrchestratorService(client.db_session)
    case_repo = CaseRepository(client.db_session)
    agent = ClientEngagementAgent(orchestrator=orchestrator, case_repo=case_repo)
    return agent, orchestrator


def test_intake_incomplete_suggestion_logs_action(client):
    case_id = _make_case(client)
    agent, orchestrator = _make_agent(client)

    result = agent.suggest_intake_incomplete_reminder(case_id, tenant_id=client.default_tenant.id, db_session=client.db_session)
    assert result["suggestion"]["message_type"] == "intake_incomplete_reminder"
    assert result["suggestion"]["requires_approval"] is True

    actions = orchestrator.fetch_actions(case_id=case_id, tenant_id=client.default_tenant.id)
    assert any(a.action_type == "intake_incomplete_reminder_suggestion" for a in actions)


def test_missing_docs_suggestion_logs_action(client):
    case_id = _make_case(client)
    agent, orchestrator = _make_agent(client)

    result = agent.suggest_missing_docs_reminder(case_id, tenant_id=client.default_tenant.id, db_session=client.db_session)
    assert result["suggestion"]["message_type"] == "missing_documents_reminder"
    assert result["suggestion"]["requires_approval"] is True

    actions = orchestrator.fetch_actions(case_id=case_id, tenant_id=client.default_tenant.id)
    assert any(a.action_type == "missing_documents_reminder_suggestion" for a in actions)


def test_client_question_reply_suggestion_logs_action(client):
    case_id = _make_case(client)
    agent, orchestrator = _make_agent(client)

    question = "How long does the review take?"
    result = agent.suggest_client_question_reply(
        case_id, tenant_id=client.default_tenant.id, question_text=question, db_session=client.db_session
    )
    assert result["suggestion"]["message_type"] == "client_question_reply"
    assert question in result["suggestion"]["body"]
    assert result["suggestion"]["requires_approval"] is True

    actions = orchestrator.fetch_actions(case_id=case_id, tenant_id=client.default_tenant.id)
    assert any(a.action_type == "client_question_reply_suggestion" for a in actions)

