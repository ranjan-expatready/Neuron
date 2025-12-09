from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.app.db.database import Base, SessionLocal, engine
from src.app.main import app
from src.app.models.tenant import Tenant
from src.app.models.user import User

client = TestClient(app)


@pytest.fixture(scope="function")
def tenant_user():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        tenant = Tenant(name="History Tenant", plan_code="pro")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        user = User(
            email="history@example.com",
            full_name="History User",
            hashed_password="hashed",
            tenant_id=tenant.id,
            role="admin",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        yield tenant.id, user.id
    finally:
        db.close()


def _eligible_payload(tenant_id: str, user_id: str):
    today = date.today()
    return {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "case_type": "express_entry_basic",
        "profile": {
            "marital_status": "single",
            "family_size": 1,
            "education": [{"level": "bachelor"}],
            "language_tests": [
                {
                    "test_type": "IELTS",
                    "listening_clb": 9,
                    "reading_clb": 9,
                    "writing_clb": 9,
                    "speaking_clb": 9,
                    "expiry_date": (today + timedelta(days=365)).isoformat(),
                }
            ],
            "work_experience": [
                {
                    "teer_level": 1,
                    "start_date": (today - timedelta(days=365)).isoformat(),
                    "end_date": today.isoformat(),
                    "is_continuous": True,
                    "is_canadian": True,
                }
            ],
            "proof_of_funds": [{"amount": 20000, "currency": "CAD", "as_of_date": today.isoformat()}],
        }
    }


def test_case_history_persists_snapshot_and_event(tenant_user):
    tenant_id, user_id = tenant_user
    response = client.post("/api/v1/cases/evaluate", json=_eligible_payload(tenant_id, user_id))
    assert response.status_code == 200
    body = response.json()
    case_id = body["case_id"]
    assert case_id
    assert body["version"] == 1

    list_response = client.get("/api/v1/case-history", params={"tenant_id": tenant_id})
    assert list_response.status_code == 200
    summaries = list_response.json()
    assert any(item["id"] == case_id for item in summaries)

    detail_response = client.get(
        f"/api/v1/case-history/{case_id}", params={"tenant_id": tenant_id}
    )
    assert detail_response.status_code == 200
    detail = detail_response.json()

    assert detail["record"]["id"] == case_id
    assert detail["snapshots"], "Expected at least one snapshot"
    assert detail["snapshots"][0]["version"] == 1
    assert detail["events"], "Expected at least one audit event"
    assert detail["events"][0]["event_type"] == "EVALUATION_CREATED"

