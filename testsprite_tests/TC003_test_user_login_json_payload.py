import requests
from config import (
    API_BASE_URL,
    LOGIN_JSON_ENDPOINT,
    REQUEST_TIMEOUT,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
)


def test_user_login_json_payload():
    url = API_BASE_URL + LOGIN_JSON_ENDPOINT

    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # Expect a successful login to return some form of token or success indication
    # Since API schema does not specify exact response body, check presence of common tokens
    assert (
        "access_token" in data or "token" in data or "user" in data
    ), "Response JSON missing expected login token or user data"


test_user_login_json_payload()
