import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.app.api.dependencies import get_current_user
from src.app.cases.repository import CaseRepository
from src.app.models.user import User


def _create_case_record(db_session, tenant_id: str):
    repo = CaseRepository(db_session)
    record = repo.create_case(
        profile={"profile": {"personal": {"given_name": "John", "family_name": "Doe"}}},
        program_eligibility={},
        crs_breakdown=None,
        required_artifacts=None,
        config_fingerprint={},
        source="test",
        status="active",
        tenant_id=tenant_id,
    )
    db_session.commit()
    return record


def test_submission_prep_happy_path(client: TestClient, admin_headers):
    """Test successful submission preparation API call."""
    record = _create_case_record(client.db_session, tenant_id=str(client.default_tenant.id))

    # Mock the engine to avoid complex setup
    with patch('src.app.services.submission_prep_engine.SubmissionPrepEngine') as mock_engine_class:
        mock_engine = mock_engine_class.return_value
        mock_result = {
            "case_id": record.id,
            "program_code": "EE_FSW",
            "form_bundle_id": "test_bundle",
            "forms": [
                {
                    "form_code": "IMM0008",
                    "form_name": "Application for Permanent Residence",
                    "fields": [
                        {
                            "field_code": "given_name",
                            "field_name": "Given Name",
                            "resolved_value": "John",
                            "source": "autofill_mapping",
                            "status": "resolved",
                            "reason": None,
                        }
                    ],
                    "attachment_required": True,
                    "status": "resolved",
                }
            ],
            "document_attachments": [
                {
                    "document_type": "IMM0008",
                    "required_for_form": "IMM0008",
                    "attached_document_ids": ["doc1"],
                    "status": "attached",
                    "reason": None,
                }
            ],
            "blocking_gaps": [],
            "summary_ready": True,
            "generated_at": "2025-12-13T12:00:00",
            "reasons": [],
        }
        mock_engine.prepare_submission.return_value = mock_result

        resp = client.get(
            f"/api/v1/cases/{record.id}/submission/prep",
            params={"program_code": "EE_FSW"},
            headers=admin_headers,
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["case_id"] == record.id
        assert body["program_code"] == "EE_FSW"
        assert body["summary_ready"] is True
        assert len(body["forms"]) == 1
        assert len(body["document_attachments"]) == 1
        assert body["blocking_gaps"] == []


def test_submission_prep_forbidden_for_non_rcic(client: TestClient):
    """Test that submission prep requires RCIC/admin access."""
    record = _create_case_record(client.db_session, tenant_id=str(client.default_tenant.id))

    def _client_user():
        return User(
            id=str(uuid.uuid4()),
            email="client@example.com",
            tenant_id=str(client.default_tenant.id),
            role="client",
        )

    client.app.dependency_overrides[get_current_user] = _client_user
    try:
        resp = client.get(f"/api/v1/cases/{record.id}/submission/prep")
        assert resp.status_code == 403
        body = resp.json()
        assert "forbidden" in body["error"]
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)


def test_submission_prep_missing_case_returns_400(client: TestClient, admin_headers):
    """Test error handling for non-existent case."""
    resp = client.get(
        "/api/v1/cases/00000000-0000-0000-0000-000000000000/submission/prep",
        headers=admin_headers,
    )
    assert resp.status_code == 400
    body = resp.json()
    assert "detail" in body


def test_submission_prep_with_bundle_id(client: TestClient, admin_headers):
    """Test submission prep with explicit bundle ID parameter."""
    record = _create_case_record(client.db_session, tenant_id=str(client.default_tenant.id))

    with patch('src.app.services.submission_prep_engine.SubmissionPrepEngine') as mock_engine_class:
        mock_engine = mock_engine_class.return_value
        mock_result = {
            "case_id": record.id,
            "program_code": None,
            "form_bundle_id": "custom_bundle",
            "forms": [],
            "document_attachments": [],
            "blocking_gaps": [],
            "summary_ready": False,
            "generated_at": "2025-12-13T12:00:00",
            "reasons": ["No forms in bundle"],
        }
        mock_engine.prepare_submission.return_value = mock_result

        resp = client.get(
            f"/api/v1/cases/{record.id}/submission/prep",
            params={"bundle_id": "custom_bundle"},
            headers=admin_headers,
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["form_bundle_id"] == "custom_bundle"
        mock_engine.prepare_submission.assert_called_once()
        call_kwargs = mock_engine.prepare_submission.call_args[1]
        assert call_kwargs["bundle_id"] == "custom_bundle"


def test_submission_prep_engine_error_returns_400(client: TestClient, admin_headers):
    """Test that engine errors are properly handled and returned as 400."""
    record = _create_case_record(client.db_session, tenant_id=str(client.default_tenant.id))

    with patch('src.app.services.submission_prep_engine.SubmissionPrepEngine') as mock_engine_class:
        mock_engine = mock_engine_class.return_value
        mock_engine.prepare_submission.side_effect = Exception("Engine configuration error")

        resp = client.get(
            f"/api/v1/cases/{record.id}/submission/prep",
            headers=admin_headers,
        )

        assert resp.status_code == 400
        body = resp.json()
        assert "detail" in body
