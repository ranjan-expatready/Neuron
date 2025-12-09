import requests

BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{BASE_URL}/api/v1/documents/upload"
TIMEOUT = 30


def test_upload_document_successfully():
    file_content = b"Test document content for upload"
    files = {"file": ("test_document.txt", file_content, "text/plain")}
    headers = {"Authorization": "Bearer YOUR_TOKEN"}
    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    try:
        resp_json = response.json()
    except ValueError:
        resp_json = None
    assert resp_json is not None, "Response did not contain valid JSON"


test_upload_document_successfully()
