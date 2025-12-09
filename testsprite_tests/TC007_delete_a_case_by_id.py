import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def create_case():
    url = f"{BASE_URL}/api/v1/cases"
    payload = {
        "title": "Test Case for Deletion",
        "description": "Case created for testing deletion endpoint.",
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json().get("id") or response.json().get("case_id") or response.json().get("id")


def delete_case(case_id):
    url = f"{BASE_URL}/api/v1/cases/{case_id}"
    headers = {"Content-Type": "application/json"}
    response = requests.delete(url, headers=headers, timeout=TIMEOUT)
    return response


def test_delete_case_by_id():
    case_id = None
    try:
        # Create a new case to have one to delete
        case_id = create_case()
        assert case_id is not None, "Failed to create a case for deletion test."

        # Delete the created case
        delete_response = delete_case(case_id)
        assert (
            delete_response.status_code == 200
        ), f"Expected status code 200 but got {delete_response.status_code}"

        # Confirm deletion by trying to get the case (expect 404)
        get_response = requests.get(f"{BASE_URL}/api/v1/cases/{case_id}", timeout=TIMEOUT)
        assert (
            get_response.status_code == 404 or get_response.status_code == 200
        ), "After deletion, case should not be found or the API returns 404."
        if get_response.status_code == 200:
            raise AssertionError("Case still exists after delete operation.")

    finally:
        # Cleanup if deletion failed or partially succeeded
        if case_id is not None:
            requests.delete(f"{BASE_URL}/api/v1/cases/{case_id}", timeout=TIMEOUT)


test_delete_case_by_id()
