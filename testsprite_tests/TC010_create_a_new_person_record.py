import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_create_new_person_record():
    url = f"{BASE_URL}/api/v1/persons"
    headers = {"Content-Type": "application/json", "Authorization": "Bearer your_access_token_here"}
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1-416-555-1234",
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        response_json = response.json()
        assert "id" in response_json, "Response missing 'id' field for created person"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"


test_create_new_person_record()
