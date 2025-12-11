import uuid

from src.app.agents.document_reviewer_agent import DocumentReviewerAgent
from src.app.models.case import Case
from src.app.models.document import Document
from src.app.services.agent_orchestrator import AgentOrchestratorService
from src.app.services.intake_engine import IntakeEngine, DocumentRequirementResolved
from src.app.services.document_content_service import DocumentContentService
from src.app.heuristics.document_heuristics import DocumentHeuristicsEngine


class _StubContentService(DocumentContentService):
    def __init__(self, text: str | None):
        super().__init__(enabled=True)
        self._text = text

    def extract_text(self, document: Document):
        return self._text


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


def _add_document(db_session, org_id: str, case_id: str, document_type: str, filename: str, mime: str = "application/pdf") -> Document:
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
        mime_type=mime,
        storage_key=f"{org_id}/{case_id}/{filename}",
        storage_provider="local",
        uploaded_by=str(uuid.uuid4()),
    )
    db_session.add(doc)
    db_session.commit()
    return doc


class _StubIntakeEngine(IntakeEngine):
    def get_document_checklist_for_profile(self, profile, program_code, db_session=None):
        return [DocumentRequirementResolved(id="passport", label="Passport", category="identity", required=True, reasons=["conditions_met"])]


class _StubHeuristicsEngine(DocumentHeuristicsEngine):
    def __init__(self):
        super().__init__()

    def analyze(self, *, doc_definition, uploaded_doc, ocr_text, canonical_profile):
        return [
            {
                "document_id": uploaded_doc.id,
                "document_type": uploaded_doc.document_type,
                "requirement_id": doc_definition.id,
                "finding_code": "passport.missing_keywords",
                "severity": "warning",
                "details": {"missing_keywords": ["surname"]},
            }
        ]


def test_document_reviewer_includes_content_warning_for_empty_text(client):
    org_id = str(client.default_org.id)
    case = _make_case(client.db_session, org_id)
    _add_document(client.db_session, org_id, case.id, "passport", "passport.pdf")

    orchestrator = AgentOrchestratorService(client.db_session)
    agent = DocumentReviewerAgent(
        orchestrator=orchestrator,
        intake_engine=_StubIntakeEngine(),
        content_service=_StubContentService(text="   "),
        heuristics_engine=_StubHeuristicsEngine(),
    )

    result = agent.review_case(
        case_id=case.id,
        tenant_id=org_id,
        db_session=client.db_session,
        program_code="EE_FSW",
        created_by_user_id=str(client.default_user.id),
    )

    warnings = result["findings"]["content_warnings"]
    assert len(warnings) == 1
    assert warnings[0]["issue"] == "empty_or_unreadable"
    heuristics = result["findings"]["heuristic_findings"]
    assert heuristics
    assert heuristics[0]["finding_code"] == "passport.missing_keywords"


def test_document_reviewer_handles_none_text_without_warning(client):
    org_id = str(client.default_org.id)
    case = _make_case(client.db_session, org_id)
    _add_document(client.db_session, org_id, case.id, "passport", "passport.pdf")

    orchestrator = AgentOrchestratorService(client.db_session)
    agent = DocumentReviewerAgent(
        orchestrator=orchestrator,
        intake_engine=_StubIntakeEngine(),
        content_service=_StubContentService(text=None),
    )

    result = agent.review_case(
        case_id=case.id,
        tenant_id=org_id,
        db_session=client.db_session,
        program_code="EE_FSW",
        created_by_user_id=str(client.default_user.id),
    )

    warnings = result["findings"]["content_warnings"]
    assert warnings == []

