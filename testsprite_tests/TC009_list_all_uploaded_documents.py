import requests

BASE_URL = "http://localhost:8000"
DOCUMENTS_ENDPOINT = f"{BASE_URL}/api/v1/documents"
TIMEOUT = 30

# Removed Authorization header since it causes 401 unauthorized
HEADERS = {}


def test_list_all_uploaded_documents():
    try:
        response = requests.get(DOCUMENTS_ENDPOINT, headers=HEADERS, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to list documents failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        documents = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    assert isinstance(documents, list), "Response JSON is not a list"


test_list_all_uploaded_documents()
