import requests

BASE_URL = "http://localhost:3000"
REGISTER_ENDPOINT = f"{BASE_URL}/api/v1/auth/register"
LOGIN_JSON_ENDPOINT = f"{BASE_URL}/api/v1/auth/login-json"
USER_PROFILE_ENDPOINT = f"{BASE_URL}/api/v1/users/me"
TIMEOUT = 30


def test_get_current_user_profile_authorized():
    test_user = {
        "email": "testuser_tc004@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "organization_name": "TestOrg",
    }

    token = None
    # Register user
    try:
        register_resp = requests.post(REGISTER_ENDPOINT, json=test_user, timeout=TIMEOUT)
        assert register_resp.status_code == 200, f"User registration failed: {register_resp.text}"

        # Login to get JWT token
        login_payload = {"email": test_user["email"], "password": test_user["password"]}
        login_resp = requests.post(LOGIN_JSON_ENDPOINT, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        login_data = login_resp.json()
        token = (
            login_data.get("access_token")
            or login_data.get("token")
            or login_data.get("accessToken")
        )
        assert token, "No token found in login response"

        headers = {"Authorization": f"Bearer {token}"}

        # Get current user profile
        profile_resp = requests.get(USER_PROFILE_ENDPOINT, headers=headers, timeout=TIMEOUT)
        assert profile_resp.status_code == 200, f"Failed to get user profile: {profile_resp.text}"
        profile_data = profile_resp.json()
        # Validate response contains expected user info
        assert profile_data.get("email") == test_user["email"], "Email in profile does not match"
        assert (
            profile_data.get("first_name") == test_user["first_name"]
        ), "First name in profile does not match"
        assert (
            profile_data.get("last_name") == test_user["last_name"]
        ), "Last name in profile does not match"
        # phone and organization_name may or may not be returned depending on schema, so check if present
        if "phone" in profile_data:
            assert (
                profile_data.get("phone") == test_user["phone"]
            ), "Phone in profile does not match"
        if "organization_name" in profile_data:
            assert (
                profile_data.get("organization_name") == test_user["organization_name"]
            ), "Organization name in profile does not match"

    finally:
        # Cleanup: delete the created user to keep test idempotent if API supports it
        # But no DELETE user endpoint in PRD, so skip cleanup or add logout if necessary
        pass


test_get_current_user_profile_authorized()
