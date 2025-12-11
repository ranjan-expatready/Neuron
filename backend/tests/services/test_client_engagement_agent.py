from io import BytesIO

from fastapi import UploadFile

from src.app.agents.client_engagement_agent import ClientEngagementAgent
from src.app.services.agent_orchestrator import AgentOrchestratorService
from src.app.cases.repository import CaseRepository
from src.app.services.document import DocumentService
from src.app.services.llm_client import LLMClient
from src.app.schemas.document import DocumentCreate


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


def _make_agent(client, llm_client: LLMClient | None = None):
    orchestrator = AgentOrchestratorService(client.db_session)
    case_repo = CaseRepository(client.db_session)
    agent = ClientEngagementAgent(orchestrator=orchestrator, case_repo=case_repo, llm_client=llm_client)
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


def test_missing_docs_excludes_already_uploaded_requirements(client):
    case_id = _make_case(client)
    agent, _ = _make_agent(client)
    repo = CaseRepository(client.db_session)
    case = repo.get_case(case_id, tenant_id=client.default_tenant.id)
    program_code = agent._infer_program(case) or "unspecified_program"  # pylint: disable=protected-access
    checklist = agent.intake_engine.get_document_checklist_for_case(
        case, program_code=program_code, db_session=client.db_session
    )
    required_req = next((r for r in checklist if r.required), None)
    assert required_req is not None
    label = required_req.label or required_req.id

    doc_service = DocumentService()
    upload = UploadFile(filename="required.pdf", file=BytesIO(b"hello"))
    doc_service.create_document(
        db=client.db_session,
        file=upload,
        document_data=DocumentCreate(
            document_type=required_req.id,
            category=required_req.category,
            title=label,
            description="test upload",
            case_id=case_id,
        ),
        org_id=str(client.default_tenant.id),
        uploaded_by=str(client.default_user.id),
        case_id=case_id,
    )
    client.db_session.commit()

    result = agent.suggest_missing_docs_reminder(
        case_id, tenant_id=client.default_tenant.id, db_session=client.db_session
    )
    missing_docs = result["suggestion"]["missing_documents"]
    assert label not in missing_docs


def test_client_question_reply_suggestion_logs_action(client):
    case_id = _make_case(client)
    llm = LLMClient(enabled=True, provider="mock", api_key="fake-key")
    agent, orchestrator = _make_agent(client, llm_client=llm)

    question = "How long does the review take?"
    result = agent.suggest_client_question_reply(
        case_id, tenant_id=client.default_tenant.id, question_text=question, db_session=client.db_session
    )
    assert result["suggestion"]["message_type"] == "client_question_reply"
    assert question in result["suggestion"]["body"]
    assert result["suggestion"]["requires_approval"] is True
    assert result["suggestion"]["llm_used"] is True

    actions = orchestrator.fetch_actions(case_id=case_id, tenant_id=client.default_tenant.id)
    assert any(a.action_type == "client_question_reply_suggestion" for a in actions)


def test_client_question_reply_falls_back_when_llm_disabled(client):
    case_id = _make_case(client)
    llm = LLMClient(enabled=False)
    agent, _ = _make_agent(client, llm_client=llm)

    question = "What documents are needed?"
    result = agent.suggest_client_question_reply(
        case_id, tenant_id=client.default_tenant.id, question_text=question, db_session=client.db_session
    )
    assert result["suggestion"]["llm_used"] is False
    assert "[AI draft]" not in result["suggestion"]["body"]

