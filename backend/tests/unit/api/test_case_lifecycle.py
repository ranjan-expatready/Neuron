from datetime import date, timedelta

from fastapi.testclient import TestClient

from src.app.cases.lifecycle_service import CaseLifecycleService
from src.app.db.database import Base, SessionLocal, engine
from src.app.main import app
from src.app.models.tenant import Tenant
from src.app.models.user import User

client = TestClient(app)


def _bootstrap_case():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    tenant = Tenant(name="Tenant API", plan_code="pro")
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


def test_case_lifecycle_blocked_when_plan_disables_feature():
    # Create case under pro, then downgrade plan to starter and attempt transition
    case_id, user_id, tenant_id = _bootstrap_case()
    db = SessionLocal()
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    tenant.plan_code = "starter"
    db.commit()
    db.close()

    response = client.post(
        f"/api/v1/case-lifecycle/{case_id}/review",
        json={"user_id": user_id, "tenant_id": tenant_id},
    )
    assert response.status_code in (400, 403)
    assert "lifecycle" in response.json().get("detail", "").lower()

