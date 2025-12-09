import requests
from config import (
    API_BASE_URL,
    LOGIN_JSON_ENDPOINT,
    REQUEST_TIMEOUT,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
)


def test_login_with_valid_credentials():
    url = API_BASE_URL + LOGIN_JSON_ENDPOINT
    headers = {"Content-Type": "application/json"}
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to login endpoint failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    try:
        json_response = response.json()
    except ValueError:
        assert False, "Response is not JSON"

    # Validate JWT token presence in response (assuming token is in a field named 'access_token' or 'token')
    token = json_response.get("access_token") or json_response.get("token")
    assert (
        token is not None and isinstance(token, str) and len(token) > 0
    ), "JWT token not found or invalid in response"


test_login_with_valid_credentials()
