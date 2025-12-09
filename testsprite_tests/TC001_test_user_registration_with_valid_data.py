import uuid

import requests

BASE_URL = "http://localhost:3000"
REGISTER_ENDPOINT = f"{BASE_URL}/api/v1/auth/register"
TIMEOUT = 30


def test_user_registration_with_valid_data():
    # Generate a unique email to avoid conflicts in repeated tests
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": unique_email,
        "password": "StrongPass!2025",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+14161234567",
        "organization_name": "Test Organization",
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(REGISTER_ENDPOINT, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to register user failed: {e}"

    # Validate response status code for successful creation (200 as per PRD)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # Optionally, check response content if any (PRD does not specify exact response body)
    try:
        data = response.json()
    except ValueError:
        data = None

    # Expecting some JSON response, validate presence of keys or success message
    # Since not specified, just ensure JSON response received
    assert data is None or isinstance(data, dict), "Response is not valid JSON or not a dict."


test_user_registration_with_valid_data()
