from datetime import date, timedelta

from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def _eligible_payload():
    today = date.today()
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


def test_case_history_persists_snapshot_and_event():
    response = client.post("/api/v1/cases/evaluate", json=_eligible_payload())
    assert response.status_code == 200
    body = response.json()
    case_id = body["case_id"]
    assert case_id
    assert body["version"] == 1

    list_response = client.get("/api/v1/case-history")
    assert list_response.status_code == 200
    summaries = list_response.json()
    assert any(item["id"] == case_id for item in summaries)

    detail_response = client.get(f"/api/v1/case-history/{case_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()

    assert detail["record"]["id"] == case_id
    assert detail["snapshots"], "Expected at least one snapshot"
    assert detail["snapshots"][0]["version"] == 1
    assert detail["events"], "Expected at least one audit event"
    assert detail["events"][0]["event_type"] == "EVALUATION_CREATED"

