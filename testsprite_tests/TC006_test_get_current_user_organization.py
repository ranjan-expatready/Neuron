import uuid

import requests

base_url = "http://localhost:3000"
timeout = 30


def test_get_current_user_organization():
    # Test user credentials and registration data
    test_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    # Ensure password length <= 72 characters (bcrypt limit)
    raw_password = "TestPass123!"
    test_password = raw_password[:72]
    test_first_name = "Test"
    test_last_name = "User"
    test_phone = "1234567890"
    test_org_name = f"TestOrg_{uuid.uuid4().hex[:8]}"

    # Register a new user
    register_url = f"{base_url}/api/v1/auth/register"
    register_payload = {
        "email": test_email,
        "password": test_password,
        "first_name": test_first_name,
        "last_name": test_last_name,
        "phone": test_phone,
        "organization_name": test_org_name,
    }
    try:
        reg_response = requests.post(register_url, json=register_payload, timeout=timeout)
        assert reg_response.status_code == 200, f"Register failed: {reg_response.text}"
    except Exception as e:
        raise AssertionError(f"Exception during user registration: {e}")

    # Login to get JWT token
    login_url = f"{base_url}/api/v1/auth/login-json"
    login_payload = {"email": test_email, "password": test_password}
    try:
        login_response = requests.post(login_url, json=login_payload, timeout=timeout)
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        login_data = login_response.json()
        token = login_data.get("access_token") or login_data.get("token")
        assert token is not None, "No access token returned on login"
    except Exception as e:
        raise AssertionError(f"Exception during user login: {e}")

    headers = {"Authorization": f"Bearer {token}"}

    # Call GET /api/v1/organizations/me to get current user's organization details
    org_me_url = f"{base_url}/api/v1/organizations/me"
    try:
        org_response = requests.get(org_me_url, headers=headers, timeout=timeout)
        assert org_response.status_code == 200, f"Get organization failed: {org_response.text}"
        org_data = org_response.json()
        # Validate returned organization details
        assert isinstance(org_data, dict), "Organization data is not a dictionary"
        # Organization must have at least name matching the registered org name
        assert "name" in org_data, "Organization name not in response"
        assert (
            org_data["name"] == test_org_name
        ), "Organization name does not match registered organization"
    except Exception as e:
        raise AssertionError(f"Exception during get current user organization: {e}")


# Call the test function
test_get_current_user_organization()
