import uuid

from fastapi.testclient import TestClient

from src.app.models.case import Case
from src.app.models.document import Document
from src.app.api.dependencies import get_current_user
from src.app.models.user import User


def _make_case(db_session, org_id: str, case_type: str = "EE_FSW") -> Case:
    case = Case(
        id=str(uuid.uuid4()),
        org_id=org_id,
        primary_person_id=str(uuid.uuid4()),
        case_type=case_type,
        title="Doc Review Case",
        description="",
        notes="",
        form_data={},
        case_number="CN-DR-1",
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


def test_document_review_api_success(client: TestClient, admin_headers):
    org_id = str(client.default_org.id)
    case = _make_case(client.db_session, org_id)
    _add_document(client.db_session, org_id, case.id, "passport", "passport.pdf")

    resp = client.post(
        "/api/v1/admin/agents/document-review",
        headers=admin_headers,
        json={"case_id": case.id, "program_code": "EE_FSW"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["case_id"] == case.id
    assert data["program_code"] == "EE_FSW"
    assert "agent_action_id" in data
    assert isinstance(data["findings"], dict)


def test_document_review_api_rbac(client: TestClient):
    # override user to non-admin
    def _agent_user():
        return User(id=str(uuid.uuid4()), email="agent@example.com", tenant_id=str(uuid.uuid4()), role="agent")

    client.app.dependency_overrides[get_current_user] = _agent_user
    try:
        resp = client.post("/api/v1/admin/agents/document-review", json={"case_id": str(uuid.uuid4())})
        assert resp.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

