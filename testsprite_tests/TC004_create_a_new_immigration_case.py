import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Assuming authentication is required, define credentials here
AUTH_URL = f"{BASE_URL}/api/v1/auth/login-json"
USERNAME = "testuser@example.com"
PASSWORD = "TestPassword123!"


def authenticate():
    try:
        resp = requests.post(
            AUTH_URL, json={"username": USERNAME, "password": PASSWORD}, timeout=TIMEOUT
        )
        resp.raise_for_status()
        token = resp.json().get("access_token")
        if not token:
            raise Exception("Authentication token not found in response")
        return token
    except Exception as e:
        raise Exception(f"Authentication failed: {str(e)}")


def test_create_new_immigration_case():
    token = authenticate()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    create_url = f"{BASE_URL}/api/v1/cases"

    # Minimal valid payload for creating a case (based on common case management info)
    payload = {
        "title": "Test Immigration Case",
        "description": "This is a test immigration case created by automated test.",
        "program": "Express Entry",  # Example field - assumed supported by the backend
    }

    created_case_id = None
    try:
        response = requests.post(create_url, json=payload, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        case_data = response.json()
        assert isinstance(case_data, dict), "Response is not a JSON object"
        # Validate some expected fields in the response
        assert "id" in case_data and case_data["id"], "Created case id missing in response"
        assert (
            "title" in case_data and case_data["title"] == payload["title"]
        ), "Case title mismatch"
        created_case_id = case_data["id"]
    finally:
        # Clean up: delete the created case if possible
        if created_case_id:
            delete_url = f"{BASE_URL}/api/v1/cases/{created_case_id}"
            try:
                del_resp = requests.delete(delete_url, headers=headers, timeout=TIMEOUT)
                # Allow 200 or 404 if already deleted
                assert del_resp.status_code in (
                    200,
                    404,
                ), f"Failed to delete created case, status code {del_resp.status_code}"
            except Exception:
                pass


test_create_new_immigration_case()
