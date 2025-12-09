import uuid

import requests

BASE_URL = "http://localhost:8000"
REGISTER_ENDPOINT = "/api/v1/auth/register"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 30


def test_register_new_user_successfully():
    # Generate unique email for testing
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": unique_email,
        "password": "StrongPassw0rd!",
        "first_name": "Test",
        "last_name": "User",
    }

    try:
        response = requests.post(
            f"{BASE_URL}{REGISTER_ENDPOINT}", headers=HEADERS, json=payload, timeout=TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}"
        # Optionally check response content if any
        # data = response.json()
        # assert "id" in data or "user" in data, "Response missing user id or info"
    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"


test_register_new_user_successfully()
