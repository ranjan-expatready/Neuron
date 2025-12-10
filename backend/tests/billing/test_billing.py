from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from src.app.schemas.person import PersonCreate
from src.app.services.billing_service import BillingService
from src.app.services.person import PersonService


def _eligible_payload():
    today = datetime.utcnow().date()
    return {
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


def _create_person(db_session, org_id: str):
    person_payload = PersonCreate(
        first_name="Test",
        last_name="User",
        email="person@example.com",
    )
    return PersonService.create_person(db_session, person_payload, org_id)


def test_billing_state_read_write(client: TestClient):
    service = BillingService(client.db_session)
    tenant_id = client.default_tenant.id
    status = service.get_plan_status(tenant_id)
    assert status["plan_code"] == service.plan_config.get("default_plan", "starter")

    updated = service.set_plan_status(tenant_id, "trial", subscription_status="trialing")
    assert updated["state"]["plan_code"] == "trial"
    assert updated["state"]["subscription_status"] == "trialing"


def test_usage_recording(client: TestClient):
    service = BillingService(client.db_session)
    tenant_id = client.default_tenant.id
    service.set_plan_status(tenant_id, "trial")
    counters = service.record_usage_event(tenant_id, "case_created")
    assert counters["case_created"]["total"] == 1


def test_admin_billing_endpoints(client: TestClient, admin_headers):
    # Default admin overrides auth; headers kept for parity with other tests
    state_resp = client.get("/api/v1/admin/billing/state", headers=admin_headers)
    assert state_resp.status_code == 200
    usage_resp = client.get("/api/v1/admin/billing/usage", headers=admin_headers)
    assert usage_resp.status_code == 200

    update_resp = client.post(
        "/api/v1/admin/billing/update-plan",
        json={"plan_code": "pro", "subscription_status": "active"},
        headers=admin_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["state"]["plan_code"] == "pro"

    portal_resp = client.get("/api/v1/admin/billing/portal-url", headers=admin_headers)
    assert portal_resp.status_code == 200
    assert "portal_url" in portal_resp.json()


def test_plan_enforcement_case_limits(client: TestClient, admin_headers):
    service = BillingService(client.db_session)
    tenant_id = client.default_tenant.id
    service.set_plan_status(tenant_id, "trial")
    service.record_usage_event(tenant_id, "case_created")

    person = _create_person(client.db_session, str(client.default_org.id))
    payload = {
        "case_type": "express_entry",
        "title": "My Case",
        "primary_person_id": str(person.id),
    }
    resp = client.post("/api/v1/cases/", json=payload, headers=admin_headers)
    assert resp.status_code == 403
    body = resp.json()
    assert body.get("error") == "plan_limit_exceeded"


def test_limit_violations_on_evaluation(client: TestClient, admin_headers):
    service = BillingService(client.db_session)
    tenant_id = client.default_tenant.id
    service.set_plan_status(tenant_id, "trial")
    service.record_usage_event(tenant_id, "evaluation_run")

    resp = client.post("/api/v1/cases/evaluate", json=_eligible_payload(), headers=admin_headers)
    assert resp.status_code == 403
    assert resp.json().get("error") == "plan_limit_exceeded"

