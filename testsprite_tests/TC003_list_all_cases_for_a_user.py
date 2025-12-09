import requests
from config import (
    API_BASE_URL,
    LOGIN_JSON_ENDPOINT,
    REQUEST_TIMEOUT,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
)


def test_list_all_cases_for_user():
    login_url = f"{API_BASE_URL}{LOGIN_JSON_ENDPOINT}"
    cases_url = f"{API_BASE_URL}/api/v1/cases"

    login_payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    }
    try:
        login_response = requests.post(login_url, json=login_payload, timeout=REQUEST_TIMEOUT)
        assert (
            login_response.status_code == 200
        ), f"Login failed with status {login_response.status_code}"
        token = login_response.json().get("access_token") or login_response.json().get("token")
        assert token, "JWT token not found in login response"

        headers = {"Authorization": f"Bearer {token}"}

        cases_response = requests.get(cases_url, headers=headers, timeout=REQUEST_TIMEOUT)
        assert (
            cases_response.status_code == 200
        ), f"Failed to list cases: {cases_response.status_code}"

        cases_data = cases_response.json()
        assert isinstance(cases_data, list), "Cases response is not a list"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"


test_list_all_cases_for_user()
