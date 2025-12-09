import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Assumed valid auth token for tests
AUTH_HEADERS = {"Authorization": "Bearer valid_token", "Content-Type": "application/json"}


def test_get_case_details_by_case_id():
    # Create a new case to ensure a valid case_id exists for testing
    create_url = f"{BASE_URL}/api/v1/cases"

    new_case_payload = {
        "title": "Test Case for TC005",
        "description": "This is a test case created for TC005.",
        "program": "Express Entry",
        "status": "open",
    }
    case_id = None

    try:
        # Create case
        create_resp = requests.post(
            create_url, json=new_case_payload, headers=AUTH_HEADERS, timeout=TIMEOUT
        )
        assert (
            create_resp.status_code == 200
        ), f"Failed to create case for test setup: {create_resp.text}"
        created_case = create_resp.json()
        case_id = created_case.get("id")
        assert case_id is not None, "Created case does not have an ID"

        # Test GET /api/v1/cases/{case_id} for existing case (expect 200)
        get_url = f"{BASE_URL}/api/v1/cases/{case_id}"
        get_resp = requests.get(get_url, headers=AUTH_HEADERS, timeout=TIMEOUT)
        assert (
            get_resp.status_code == 200
        ), f"Expected 200 for existing case, got {get_resp.status_code}"
        case_data = get_resp.json()
        assert case_data.get("id") == case_id, "Returned case ID does not match requested ID"

        # Test GET /api/v1/cases/{case_id} for non-existing case (expect 404)
        invalid_case_id = "nonexistent-id-123456"
        invalid_get_url = f"{BASE_URL}/api/v1/cases/{invalid_case_id}"
        invalid_get_resp = requests.get(invalid_get_url, headers=AUTH_HEADERS, timeout=TIMEOUT)
        assert (
            invalid_get_resp.status_code == 404
        ), f"Expected 404 for non-existing case, got {invalid_get_resp.status_code}"

    finally:
        # Clean up created case
        if case_id:
            delete_url = f"{BASE_URL}/api/v1/cases/{case_id}"
            try:
                requests.delete(delete_url, headers=AUTH_HEADERS, timeout=TIMEOUT)
            except Exception:
                pass


test_get_case_details_by_case_id()
