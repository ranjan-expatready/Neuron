import uuid

from fastapi.testclient import TestClient

from src.app.api.dependencies import get_current_user
from src.app.cases.repository import CaseRepository
from src.app.models.user import User
from src.app.config.form_config import clear_caches as clear_form_caches


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


def test_forms_autofill_preview_happy_path(client: TestClient, admin_headers):
    clear_form_caches()
    record = _create_case_record(client.db_session, tenant_id=str(client.default_tenant.id))

    resp = client.get(
        f"/api/v1/cases/{record.id}/forms/autofill-preview",
        params={"program_code": "EE_FSW"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["bundle_id"] in (None, "ee_fsw_base_package")
    form = next(f for f in body["forms"] if f["form_id"] == "IMM0008")
    given = next(f for f in form["fields"] if f["field_id"] == "given_name")
    assert given["proposed_value"] == "John"
    assert given["source_type"] == "canonical_profile"


def test_forms_autofill_preview_forbidden_for_non_rcic(client: TestClient):
    clear_form_caches()
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
        resp = client.get(f"/api/v1/cases/{record.id}/forms/autofill-preview")
        assert resp.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)


def test_forms_autofill_preview_missing_case_returns_404(client: TestClient, admin_headers):
    clear_form_caches()
    resp = client.get(
        "/api/v1/cases/00000000-0000-0000-0000-000000000000/forms/autofill-preview",
        headers=admin_headers,
    )
    assert resp.status_code == 400 or resp.status_code == 404

