from fastapi.testclient import TestClient

from src.app.cases.repository import CaseRepository
from src.app.services.intake_engine import clear_intake_config_cache


def _seed_case(client: TestClient, program_code: str = "EE_FSW") -> str:
    repo = CaseRepository(client.db_session)
    record = repo.create_case(
        profile={"profile": {"family": {"size": 2}, "personal": {"citizenship": "INDIA"}}},
        program_eligibility={"results": [{"program_code": program_code, "eligible": True}]},
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
    return record.id


def test_get_intake_schema(client: TestClient, admin_headers):
    clear_intake_config_cache()
    response = client.get("/api/v1/intake-schema", params={"program_code": "EE_FSW"}, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["program_code"] == "EE_FSW"
    assert data["steps"]
    assert data["steps"][0]["fields"]
    # select options hydrated from options_ref
    select_fields = [f for f in data["steps"][0]["fields"] if f["ui_control"] == "select"]
    if select_fields:
        assert select_fields[0].get("options") is not None


def test_get_document_checklist(client: TestClient, admin_headers):
    clear_intake_config_cache()
    case_id = _seed_case(client)
    response = client.get(f"/api/v1/document-checklist/{case_id}", headers=admin_headers)
    assert response.status_code == 200
    checklist = response.json()
    ids = {item["id"] for item in checklist}
    assert "passport_main" in ids
    assert any(item["id"] == "proof_of_funds" and item["required"] for item in checklist)


def test_get_intake_options(client: TestClient, admin_headers):
    response = client.get("/api/v1/intake-options", params={"name": "marital_status"}, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(opt["value"] == "single" for opt in data)


def test_intake_schema_respects_active_overrides(client: TestClient, admin_headers):
    clear_intake_config_cache()
    # insert active draft override
    from src.app.models.intake_config_draft import IntakeConfigDraft
    import uuid

    override = IntakeConfigDraft(
        config_type="field",
        key="person.date_of_birth",
        payload={
            "id": "person.date_of_birth",
            "label": "DOB Override",
            "data_path": "profile.personal.date_of_birth",
            "type": "date",
            "ui_control": "date",
        },
        status="active",
        created_by="tester",
        updated_by="tester",
    )
    client.db_session.add(override)
    client.db_session.commit()

    resp = client.get("/api/v1/intake-schema", params={"program_code": "EE_FSW"}, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    labels = [f["label"] for step in data["steps"] for f in step["fields"] if f["id"] == "person.date_of_birth"]
    assert "DOB Override" in labels

