import requests

BASE_URL = "http://localhost:3000"
REGISTER_ENDPOINT = f"{BASE_URL}/api/v1/auth/register"
LOGIN_ENDPOINT = f"{BASE_URL}/api/v1/auth/login-json"
USER_PROFILE_ENDPOINT = f"{BASE_URL}/api/v1/users/me"
TIMEOUT = 30


def test_update_current_user_profile_authorized():
    # Test data for user registration
    user_data = {
        "email": "test_update_user@example.com",
        "password": "StrongPass!1"[:72],  # Truncate password to 72 bytes limit
        "first_name": "Test",
        "last_name": "User",
        "phone": "123-456-7890",
        "organization_name": "Test Organization",
    }

    # Updated user profile data
    updated_profile_data = {
        "first_name": "UpdatedTest",
        "last_name": "UpdatedUser",
        "phone": "098-765-4321",
        "organization_name": "Updated Organization",
    }

    # Headers for JSON payloads
    headers = {"Content-Type": "application/json"}

    # Register the user (clean up by deleting user is not exposed in doc, so just register unique email)
    register_response = requests.post(
        REGISTER_ENDPOINT, json=user_data, headers=headers, timeout=TIMEOUT
    )
    assert (
        register_response.status_code == 200
    ), f"User registration failed: {register_response.text}"

    try:
        # Login to get auth token
        login_payload = {"email": user_data["email"], "password": user_data["password"]}
        login_response = requests.post(
            LOGIN_ENDPOINT, json=login_payload, headers=headers, timeout=TIMEOUT
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        login_json = login_response.json()
        assert "access_token" in login_json, "No access_token in login response"
        token = login_json["access_token"]

        auth_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Update user profile endpoint with PUT method
        update_response = requests.put(
            USER_PROFILE_ENDPOINT, json=updated_profile_data, headers=auth_headers, timeout=TIMEOUT
        )
        assert update_response.status_code == 200, f"Profile update failed: {update_response.text}"
        update_json = update_response.json()

        # Validate updated fields are reflected in response
        for key, value in updated_profile_data.items():
            assert key in update_json, f"{key} not in update response"
            assert update_json[key] == value, f"{key} not updated correctly"

        # Additionally, GET profile to confirm update
        get_response = requests.get(USER_PROFILE_ENDPOINT, headers=auth_headers, timeout=TIMEOUT)
        assert get_response.status_code == 200, f"Get profile failed: {get_response.text}"
        get_json = get_response.json()
        for key, value in updated_profile_data.items():
            assert key in get_json, f"{key} not in get profile response"
            assert get_json[key] == value, f"{key} value mismatch in get profile"

    finally:
        # No user deletion endpoint provided, so cannot clean up user created
        pass


test_update_current_user_profile_authorized()
