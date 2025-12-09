import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}


def create_case():
    url = f"{BASE_URL}/api/v1/cases"
    payload = {
        "title": "Test Case for Update",
        "description": "Initial description for test case update",
        "status": "open",
    }
    response = requests.post(url, json=payload, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    return data.get("id")


def delete_case(case_id):
    url = f"{BASE_URL}/api/v1/cases/{case_id}"
    response = requests.delete(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()


def test_update_existing_case():
    case_id = None
    try:
        # Create a case to update
        case_id = create_case()
        assert case_id is not None, "Failed to create initial case for update test"

        # Prepare update payload
        update_payload = {
            "title": "Updated Test Case Title",
            "description": "Updated description for test case",
            "status": "in_progress",
        }

        # Update the case
        update_url = f"{BASE_URL}/api/v1/cases/{case_id}"
        update_response = requests.put(
            update_url, json=update_payload, headers=HEADERS, timeout=TIMEOUT
        )

        # Assert update response status code
        assert (
            update_response.status_code == 200
        ), f"Expected status code 200, got {update_response.status_code}"

        # Optionally verify the updated content by retrieving the case details
        get_response = requests.get(update_url, headers=HEADERS, timeout=TIMEOUT)
        assert (
            get_response.status_code == 200
        ), f"Expected status code 200 on GET after update, got {get_response.status_code}"
        case_data = get_response.json()

        assert case_data.get("title") == update_payload["title"], "Title was not updated correctly"
        assert (
            case_data.get("description") == update_payload["description"]
        ), "Description was not updated correctly"
        assert (
            case_data.get("status") == update_payload["status"]
        ), "Status was not updated correctly"

    finally:
        if case_id:
            try:
                delete_case(case_id)
            except Exception:
                pass


test_update_existing_case()
