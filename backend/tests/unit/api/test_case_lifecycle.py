from datetime import date, timedelta

from fastapi.testclient import TestClient

from src.app.cases.lifecycle_service import CaseLifecycleService
from src.app.db.database import SessionLocal
from src.app.main import app
from src.app.models.tenant import Tenant
from src.app.models.user import User

client = TestClient(app)


def _bootstrap_case():
    db = SessionLocal()
    tenant = Tenant(name="Tenant API")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    user = User(
        email="api@example.com",
        full_name="API User",
        hashed_password="hash",
        tenant_id=tenant.id,
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

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
        tenant_id=tenant.id,
        user_id=user.id,
        source="api_test",
    )
    case_id = case.id
    user_id = user.id
    tenant_id = tenant.id
    db.close()
    return case_id, user_id, tenant_id


def test_case_lifecycle_submit_endpoint():
    case_id, user_id, tenant_id = _bootstrap_case()
    response = client.post(
        f"/api/v1/case-lifecycle/{case_id}/submit",
        json={"user_id": user_id, "tenant_id": tenant_id},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["record"]["status"] == "submitted"
    assert body["last_snapshot_version"] >= 1
    assert body["events"]

