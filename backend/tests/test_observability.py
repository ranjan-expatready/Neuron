from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def test_request_id_header_present():
    resp = client.get("/internal/healthz")
    assert resp.status_code == 200
    assert resp.headers.get("X-Request-ID")


def test_health_endpoints():
    resp = client.get("/internal/healthz")
    assert resp.status_code == 200
    assert resp.json().get("status") == "ok"

    ready = client.get("/internal/readyz")
    assert ready.status_code == 200
    assert ready.json().get("status") == "ready"


def test_metrics_endpoint():
    resp = client.get("/internal/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert "requests_total" in body
    assert "requests_failed_total" in body
    assert "billing_events_total" in body
    assert "plan_limit_violations_total" in body
