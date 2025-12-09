import requests
from config import (
    API_BASE_URL,
    LOGIN_JSON_ENDPOINT,
    REQUEST_TIMEOUT,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
)


def test_user_login_with_valid_credentials():
    login_url = f"{API_BASE_URL}{LOGIN_JSON_ENDPOINT}"

    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(login_url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        json_response = response.json()
        token = json_response.get("access_token") or json_response.get("token")
        assert token and isinstance(token, str), "Login response missing token"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"


test_user_login_with_valid_credentials()
