import datetime

from src.app.agents.client_engagement_agent import ClientEngagementAgent
from src.app.services.agent_orchestrator import AgentOrchestratorService
from src.app.services.client_engagement_auto_runner import ClientEngagementAutoRunner
from src.app.services.client_engagement_settings_service import ClientEngagementSettingsService
from src.app.cases.repository import CaseRepository


def _make_case(client):
    repo = CaseRepository(client.db_session)
    case = repo.create_case(
        profile={"profile": {"personal": {"citizenship": "INDIA"}, "client_name": "Alex"}},
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


def test_auto_runner_sends_when_enabled(client):
    case_id = _make_case(client)
    orchestrator = AgentOrchestratorService(client.db_session)
    settings = ClientEngagementSettingsService(client.db_session)
    settings.update_settings(client.default_tenant.id, auto_intake_reminders_enabled=True, auto_missing_docs_reminders_enabled=True)
    agent = ClientEngagementAgent(orchestrator=orchestrator, case_repo=CaseRepository(client.db_session))
    runner = ClientEngagementAutoRunner(
        db=client.db_session,
        agent=agent,
        orchestrator=orchestrator,
        settings_service=settings,
    )

    result = runner.run_for_case(case_id, tenant_id=client.default_tenant.id, db_session=client.db_session)
    assert result["intake_sent"] or result["docs_sent"]
    actions = orchestrator.fetch_actions(case_id=case_id, tenant_id=client.default_tenant.id, status="executed", auto_mode=True)
    assert len(actions) >= 1


def test_auto_runner_respects_throttle(client):
    case_id = _make_case(client)
    orchestrator = AgentOrchestratorService(client.db_session)
    settings = ClientEngagementSettingsService(client.db_session)
    settings.update_settings(client.default_tenant.id, auto_intake_reminders_enabled=True, min_days_between_intake_reminders=10)
    agent = ClientEngagementAgent(orchestrator=orchestrator, case_repo=CaseRepository(client.db_session))
    runner = ClientEngagementAutoRunner(
        db=client.db_session,
        agent=agent,
        orchestrator=orchestrator,
        settings_service=settings,
    )

    # First run sends
    runner.run_for_case(case_id, tenant_id=client.default_tenant.id, db_session=client.db_session)
    # Second run should be throttled (no new executed actions)
    before = len(orchestrator.fetch_actions(case_id=case_id, tenant_id=client.default_tenant.id, status="executed", auto_mode=True))
    runner.run_for_case(case_id, tenant_id=client.default_tenant.id, db_session=client.db_session)
    after = len(orchestrator.fetch_actions(case_id=case_id, tenant_id=client.default_tenant.id, status="executed", auto_mode=True))
    assert after == before

