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


def test_get_document_checklist(client: TestClient, admin_headers):
    clear_intake_config_cache()
    case_id = _seed_case(client)
    response = client.get(f"/api/v1/document-checklist/{case_id}", headers=admin_headers)
    assert response.status_code == 200
    checklist = response.json()
    ids = {item["id"] for item in checklist}
    assert "passport_main" in ids
    assert any(item["id"] == "proof_of_funds" and item["required"] for item in checklist)

