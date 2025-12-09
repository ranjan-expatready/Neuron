import uuid

import requests

BASE_URL = "http://localhost:3000"
TIMEOUT = 30

# Credentials for test user (adjust accordingly)
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "TestPass123!"


def test_update_current_user_organization():
    session = requests.Session()
    try:
        # Step 1: Login to get auth token
        login_url = f"{BASE_URL}/api/v1/auth/login-json"
        login_payload = {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        login_resp = session.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        login_data = login_resp.json()
        assert "access_token" in login_data, "access_token missing in login response"
        token = login_data["access_token"]

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Step 2: Get current organization details
        get_org_url = f"{BASE_URL}/api/v1/organizations/me"
        get_org_resp = session.get(get_org_url, headers=headers, timeout=TIMEOUT)
        assert get_org_resp.status_code == 200, f"Get organization failed: {get_org_resp.text}"
        org_data = get_org_resp.json()
        assert isinstance(org_data, dict), "Organization data is not a dict"

        # Prepare update payload based on existing data, modify organization_name for test
        updated_org_data = org_data.copy()
        prefix = "UpdatedOrg-"
        # Use UUID to avoid collision and ensure change
        unique_suffix = str(uuid.uuid4())[:8]
        if "organization_name" in updated_org_data and isinstance(
            updated_org_data["organization_name"], str
        ):
            updated_org_data["organization_name"] = prefix + unique_suffix
        else:
            # If no organization_name field or invalid, add one
            updated_org_data["organization_name"] = prefix + unique_suffix

        # Step 3: Update current user's organization
        update_url = f"{BASE_URL}/api/v1/organizations/me"
        update_resp = session.put(
            update_url, headers=headers, json=updated_org_data, timeout=TIMEOUT
        )
        assert update_resp.status_code == 200, f"Update organization failed: {update_resp.text}"
        updated_response = update_resp.json()
        # Validate response updated organization_name matches the sent data
        assert "organization_name" in updated_response, "organization_name not in update response"
        assert (
            updated_response["organization_name"] == updated_org_data["organization_name"]
        ), "organization_name in response does not match updated value"

        # Step 4: Verify update by GET again
        verify_resp = session.get(get_org_url, headers=headers, timeout=TIMEOUT)
        assert verify_resp.status_code == 200, f"Verify organization get failed: {verify_resp.text}"
        verify_data = verify_resp.json()
        assert (
            verify_data.get("organization_name") == updated_org_data["organization_name"]
        ), "Verified organization_name does not match updated value"

    finally:
        session.close()


test_update_current_user_organization()
