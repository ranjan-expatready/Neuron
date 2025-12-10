from datetime import date, timedelta

from fastapi.testclient import TestClient

from src.app.cases.lifecycle_service import CaseLifecycleService
from src.app.db.database import get_db


def _bootstrap_case(db, tenant_id: str, user_id: str):
    service = CaseLifecycleService(db)
    case = service.create_case(
        profile={
            "marital_status": "single",
            "family_size": 1,
            "language_tests": [
                {
                    "test_type": "IELTS",
                    "listening_clb": 9,
                    "reading_clb": 9,
                    "writing_clb": 9,
                    "speaking_clb": 9,
                    "expiry_date": (date.today() + timedelta(days=300)).isoformat(),
                }
            ],
        },
        tenant_id=tenant_id,
        user_id=user_id,
        source="api_test",
    )
    return case.id


def test_case_lifecycle_submit_endpoint(client: TestClient, auth_headers):
    db = next(client.app.dependency_overrides[get_db]())  # type: ignore
    tenant_id = client.default_tenant.id
    user_id = client.default_user.id
    case_id = _bootstrap_case(db, tenant_id, user_id)
    response = client.post(
        f"/api/v1/case-lifecycle/{case_id}/submit",
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["record"]["status"] == "submitted"
    assert body["last_snapshot_version"] >= 1
    assert body["events"]

