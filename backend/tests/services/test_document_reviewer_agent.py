import uuid

from src.app.agents.document_reviewer_agent import DocumentReviewerAgent
from src.app.models.case import Case
from src.app.models.document import Document
from src.app.services.agent_orchestrator import AgentOrchestratorService
from src.app.services.intake_engine import IntakeEngine


def _make_case(db_session, org_id: str, case_type: str = "EE_FSW") -> Case:
    case = Case(
        id=str(uuid.uuid4()),
        org_id=org_id,
        primary_person_id=str(uuid.uuid4()),
        case_type=case_type,
        title="Test case",
        description="",
        notes="",
        form_data={},
        case_number="CN-1",
        status="active",
    )
    db_session.add(case)
    db_session.commit()
    return case


def _add_document(db_session, org_id: str, case_id: str, document_type: str, filename: str) -> Document:
    doc = Document(
        org_id=org_id,
        case_id=case_id,
        document_type=document_type,
        category="identity",
        title=document_type,
        description="",
        filename=filename,
        original_filename=filename,
        file_size=100,
        mime_type="application/pdf",
        storage_key=f"{org_id}/{case_id}/{filename}",
        storage_provider="local",
        uploaded_by=str(uuid.uuid4()),
    )
    db_session.add(doc)
    db_session.commit()
    return doc


def test_document_reviewer_agent_marks_present_and_missing(client):
    org_id = str(client.default_org.id)
    case = _make_case(client.db_session, org_id)
    _add_document(client.db_session, org_id, case.id, "passport", "passport.pdf")

    orchestrator = AgentOrchestratorService(client.db_session)
    agent = DocumentReviewerAgent(orchestrator=orchestrator, intake_engine=IntakeEngine())

    result = agent.review_case(
        case_id=case.id,
        tenant_id=org_id,
        db_session=client.db_session,
        program_code="EE_FSW",
        created_by_user_id=str(client.default_user.id),
    )

    assert result["findings"]["required_present"] or result["findings"]["optional_present"] is not None
    assert "agent_action_id" in result
    actions = orchestrator.fetch_actions(case_id=case.id, tenant_id=org_id, agent_name="document_reviewer")
    assert len(actions) == 1
    assert actions[0].status == "suggested"
    assert actions[0].auto_mode is False


def test_document_reviewer_agent_handles_missing(client):
    org_id = str(client.default_org.id)
    case = _make_case(client.db_session, org_id)

    orchestrator = AgentOrchestratorService(client.db_session)
    agent = DocumentReviewerAgent(orchestrator=orchestrator, intake_engine=IntakeEngine())

    result = agent.review_case(
        case_id=case.id,
        tenant_id=org_id,
        db_session=client.db_session,
        program_code="EE_FSW",
        created_by_user_id=str(client.default_user.id),
    )

    assert isinstance(result["findings"]["required_missing"], list)
    actions = orchestrator.fetch_actions(case_id=case.id, tenant_id=org_id, agent_name="document_reviewer")
    assert len(actions) == 1

