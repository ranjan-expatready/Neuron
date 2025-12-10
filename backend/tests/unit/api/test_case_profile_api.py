from fastapi.testclient import TestClient

from src.app.cases.repository import CaseRepository


def _seed_case(client: TestClient):
    repo = CaseRepository(client.db_session)
    record = repo.create_case(
        profile={"profile": {"personal": {"marital_status": "single"}}},
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
    return record.id


def test_get_case_profile(client: TestClient, admin_headers):
    case_id = _seed_case(client)
    resp = client.get(f"/api/v1/cases/{case_id}/profile", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["profile"]["personal"]["marital_status"] == "single"


def test_patch_case_profile_merges(client: TestClient, admin_headers):
    case_id = _seed_case(client)
    resp = client.patch(
        f"/api/v1/cases/{case_id}/profile",
        headers=admin_headers,
        json={"profile": {"personal": {"citizenship": "CANADA"}, "family": {"size": 3}}},
    )
    assert resp.status_code == 200
    profile = resp.json()["profile"]
    assert profile["personal"]["marital_status"] == "single"
    assert profile["personal"]["citizenship"] == "CANADA"
    assert profile["family"]["size"] == 3

