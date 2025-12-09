import uuid

import requests

BASE_URL = "http://localhost:3000"
TIMEOUT = 30

# Test user credentials for authentication
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "TestPassword123!"

# User registration payload required by /auth/register
TEST_USER_REG_PAYLOAD = {
    "email": TEST_USER_EMAIL,
    "password": TEST_USER_PASSWORD,
    "first_name": "Test",
    "last_name": "User",
    "phone": "+1234567890",
    "organization_name": "TestOrg",
}


def register_user_if_not_exists():
    # Attempt to register user, ignore if already exists
    url = f"{BASE_URL}/api/v1/auth/register"
    try:
        response = requests.post(url, json=TEST_USER_REG_PAYLOAD, timeout=TIMEOUT)
        if response.status_code == 200:
            return  # Successfully registered
        elif response.status_code == 400:
            # Probably user exists; ignore
            return
        else:
            response.raise_for_status()
    except requests.RequestException:
        pass  # Ignore errors on registration


def authenticate_user(email, password):
    url = f"{BASE_URL}/api/v1/auth/login-json"
    payload = {"email": email, "password": password}
    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token") or data.get("token") or data.get("accessToken")
        if not token:
            raise ValueError("Authentication token not found in response")
        return token
    except requests.RequestException as e:
        raise RuntimeError(f"Authentication failed: {e}")


def test_create_new_person():
    register_user_if_not_exists()
    token = authenticate_user(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{BASE_URL}/api/v1/persons"
    # Create a unique person record
    new_person_payload = {
        "first_name": "Test",
        "last_name": f"User{uuid.uuid4().hex[:8]}",
        "email": f"testuser{uuid.uuid4().hex[:8]}@example.com",
        "phone": "+1234567890",
        "date_of_birth": "1990-01-01",
        "gender": "unspecified",
        "address": "123 Test Street",
        "city": "Testville",
        "province": "ON",
        "country": "Canada",
        "postal_code": "A1A1A1",
    }

    created_person_id = None
    try:
        response = requests.post(url, headers=headers, json=new_person_payload, timeout=TIMEOUT)
        response.raise_for_status()

        person_data = response.json()
        created_person_id = (
            person_data.get("id") or person_data.get("person_id") or person_data.get("uuid")
        )
        assert created_person_id, "Created person ID not found in response"

        # Validate returned fields - some basic checks
        assert (
            person_data.get("first_name") == new_person_payload["first_name"]
        ), "First name mismatch"
        assert person_data.get("last_name") == new_person_payload["last_name"], "Last name mismatch"
        assert person_data.get("email") == new_person_payload["email"], "Email mismatch"

    except requests.HTTPError as he:
        assert False, f"HTTP error occurred: {he.response.status_code} - {he.response.text}"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"
    finally:
        # Cleanup: delete the created person record if created
        if created_person_id:
            try:
                delete_url = f"{BASE_URL}/api/v1/persons/{created_person_id}"
                del_response = requests.delete(delete_url, headers=headers, timeout=TIMEOUT)
                del_response.raise_for_status()
            except Exception:
                pass  # Ignore cleanup failures


test_create_new_person()
