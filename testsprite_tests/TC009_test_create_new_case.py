import random
import string

import requests

BASE_URL = "http://localhost:3000"
TIMEOUT = 30


def test_create_new_case():
    # Register a new user
    register_url = f"{BASE_URL}/api/v1/auth/register"
    # Generate unique email to avoid conflicts
    random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    user_email = f"testuser_{random_suffix}@example.com"
    user_password = "TestPass123"  # password less than 72 bytes
    register_payload = {
        "email": user_email,
        "password": user_password,
        "first_name": "Test",
        "last_name": "User",
        "phone": "123-456-7890",
        "organization_name": f"Org_{random_suffix}",
    }
    token = None
    person_id = None
    case_id = None
    try:
        r = requests.post(register_url, json=register_payload, timeout=TIMEOUT)
        assert r.status_code == 200, f"User registration failed: {r.text}"

        # Login the user to get JWT token
        login_url = f"{BASE_URL}/api/v1/auth/login-json"
        login_payload = {"email": user_email, "password": user_password}
        r = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert r.status_code == 200, f"User login failed: {r.text}"
        token = r.json().get("access_token")
        assert token, "Access token not found in login response"

        headers = {"Authorization": f"Bearer {token}"}

        # Create a new person, since case requires a person record
        create_person_url = f"{BASE_URL}/api/v1/persons"
        person_payload = {
            "first_name": "Case",
            "last_name": "Client",
            "email": f"caseclient_{random_suffix}@example.com",
            "phone": "987-654-3210",
        }
        r = requests.post(create_person_url, json=person_payload, headers=headers, timeout=TIMEOUT)
        assert r.status_code == 200, f"Create person failed: {r.text}"
        person_data = r.json()
        person_id = person_data.get("id") or person_data.get("person_id")
        assert person_id, "Person ID not returned after creation"

        # Prepare case data to create new case
        create_case_url = f"{BASE_URL}/api/v1/cases"
        user_profile_url = f"{BASE_URL}/api/v1/users/me"
        r = requests.get(user_profile_url, headers=headers, timeout=TIMEOUT)
        assert r.status_code == 200, f"Get user profile failed: {r.text}"
        user_info = r.json()
        assigned_to = user_info.get("id")
        assert assigned_to, "Current user id not found in profile"

        case_payload = {
            "person_id": person_id,
            "case_type": "PR",
            "status": "open",
            "assigned_to": assigned_to,
            "title": "Test Immigration Case",
        }

        r = requests.post(create_case_url, json=case_payload, headers=headers, timeout=TIMEOUT)
        assert r.status_code == 200, f"Create case failed: {r.text}"
        case_data = r.json()
        case_id = case_data.get("id") or case_data.get("case_id")
        assert case_id, "Case ID not returned after creation"

    finally:
        headers_auth = {"Authorization": f"Bearer {token}"} if token else {}
        if case_id:
            delete_case_url = f"{BASE_URL}/api/v1/cases/{case_id}"
            try:
                requests.delete(delete_case_url, headers=headers_auth, timeout=TIMEOUT)
            except Exception:
                pass
        if person_id:
            delete_person_url = f"{BASE_URL}/api/v1/persons/{person_id}"
            try:
                requests.delete(delete_person_url, headers=headers_auth, timeout=TIMEOUT)
            except Exception:
                pass


test_create_new_case()
