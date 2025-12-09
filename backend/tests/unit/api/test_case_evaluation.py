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
        tenant = Tenant(name="Eval Tenant", plan_code="pro")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        user = User(
            email="eval@example.com",
            full_name="Eval User",
            hashed_password="hash",
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


def test_case_evaluation_happy_path(tenant_user):
    tenant_id, user_id = tenant_user
    response = client.post("/api/v1/cases/evaluate", json=_eligible_payload(tenant_id, user_id))
    assert response.status_code == 200
    body = response.json()
    assert body["case_id"]
    assert body["version"] == 1
    assert "program_eligibility" in body
    assert any(item["eligible"] for item in body["program_eligibility"])
    assert body["crs"]["total"] >= 0
    assert len(body["documents_and_forms"].get("forms", [])) > 0
    assert body["config_version"]


def test_case_evaluation_ineligible_language(tenant_user):
    tenant_id, user_id = tenant_user
    payload = _eligible_payload(tenant_id, user_id)
    payload["profile"]["language_tests"][0]["listening_clb"] = 3
    payload["profile"]["language_tests"][0]["reading_clb"] = 3
    payload["profile"]["language_tests"][0]["writing_clb"] = 3
    payload["profile"]["language_tests"][0]["speaking_clb"] = 3

    response = client.post("/api/v1/cases/evaluate", json=payload)
    assert response.status_code == 200
    body = response.json()
    fsw = next((p for p in body["program_eligibility"] if p["program_code"] == "FSW"), None)
    assert fsw is not None
    assert fsw["eligible"] is False
    assert any("CLB" in reason.upper() for reason in fsw["reasons"])


def test_case_evaluation_warns_expiring_language(tenant_user):
    tenant_id, user_id = tenant_user
    payload = _eligible_payload(tenant_id, user_id)
    payload["profile"]["language_tests"][0]["expiry_date"] = (date.today() + timedelta(days=5)).isoformat()

    response = client.post("/api/v1/cases/evaluate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "warnings" in body
    assert body["audit"]["source"] == "express_entry_intake"

