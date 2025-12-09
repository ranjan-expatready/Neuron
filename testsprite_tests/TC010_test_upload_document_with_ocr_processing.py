import io
import uuid

import requests

BASE_URL = "http://localhost:3000"
TIMEOUT = 30


def test_upload_document_with_ocr_processing():
    # Test user credentials for login - replace with valid test credentials as appropriate
    test_email = "testuser@example.com"
    test_password = "TestPassword123!"

    # Step 1: Authenticate user to get JWT token
    auth_url = f"{BASE_URL}/api/v1/auth/login-json"
    auth_payload = {"email": test_email, "password": test_password}
    try:
        auth_resp = requests.post(auth_url, json=auth_payload, timeout=TIMEOUT)
        assert auth_resp.status_code == 200, f"Login failed with status {auth_resp.status_code}"
        auth_data = auth_resp.json()
        token = (
            auth_data.get("access_token")
            or auth_data.get("token")
            or auth_data.get("jwt")
            or auth_data.get("accessToken")
        )
        assert token is not None, "No access token received on login"
    except Exception as e:
        assert False, f"Authentication request failed: {e}"

    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Since document upload requires metadata and related IDs, create a person and a case to associate
    person_id = None
    case_id = None
    document_id = None

    try:
        # Create a person
        person_url = f"{BASE_URL}/api/v1/persons"
        person_payload = {
            "first_name": "Test",
            "last_name": "User",
            "email": f"testuser.{uuid.uuid4()}@example.com",
        }
        # This endpoint requires authentication
        person_resp = requests.post(
            person_url, json=person_payload, headers=headers, timeout=TIMEOUT
        )
        assert person_resp.status_code == 200, f"Failed to create person: {person_resp.text}"
        person_data = person_resp.json()
        person_id = person_data.get("id")
        assert person_id, "Person ID not returned on creation"

        # Create a case associated with person
        case_url = f"{BASE_URL}/api/v1/cases"
        case_payload = {
            "person_id": person_id,
            "case_type": "general",  # Assuming 'general' is a valid case type; adjust if needed
            "status": "open",
        }
        case_resp = requests.post(case_url, json=case_payload, headers=headers, timeout=TIMEOUT)
        assert case_resp.status_code == 200, f"Failed to create case: {case_resp.text}"
        case_data = case_resp.json()
        case_id = case_data.get("id")
        assert case_id, "Case ID not returned on creation"

        # Step 3: Upload a document with required metadata and file
        upload_url = f"{BASE_URL}/api/v1/documents/upload"

        # Prepare a small in-memory file for upload
        file_content = b"Test document content for OCR processing."
        file_obj = io.BytesIO(file_content)
        file_obj.name = "test_document.txt"  # Filename required by requests for multipart

        multipart_data = {
            "document_type": (None, "test_document_type"),
            "category": (None, "test_category"),
            "title": (None, "Test Document Title"),
            "description": (None, "Test document description"),
            "case_id": (None, case_id),
            "person_id": (None, person_id),
            "access_level": (None, "confidential"),
            "file": (file_obj.name, file_obj, "text/plain"),
        }

        upload_resp = requests.post(
            upload_url, files=multipart_data, headers=headers, timeout=TIMEOUT
        )
        assert upload_resp.status_code == 200, f"Document upload failed: {upload_resp.text}"
        upload_data = upload_resp.json()
        document_id = upload_data.get("id")
        assert document_id, "Document ID not returned on upload"

        # Step 4: Trigger OCR processing explicitly if needed (separate endpoint)
        ocr_url = f"{BASE_URL}/api/v1/documents/{document_id}/process-ocr"
        ocr_resp = requests.post(ocr_url, headers=headers, timeout=TIMEOUT)
        assert ocr_resp.status_code == 200, f"OCR processing request failed: {ocr_resp.text}"
        ocr_data = ocr_resp.json()
        # Assume OCR processing returns a status field or similar confirmation
        assert (
            "status" in ocr_data or "message" in ocr_data or "ocr_result" in ocr_data
        ), "OCR processing response missing expected fields"

    finally:
        # Cleanup: delete created resources in reverse order of creation to avoid dependency issues
        if document_id:
            try:
                del_doc_url = f"{BASE_URL}/api/v1/documents/{document_id}"
                del_doc_resp = requests.delete(del_doc_url, headers=headers, timeout=TIMEOUT)
                assert del_doc_resp.status_code == 200, f"Failed to delete document {document_id}"
            except Exception:
                pass
        if case_id:
            try:
                del_case_url = f"{BASE_URL}/api/v1/cases/{case_id}"
                del_case_resp = requests.delete(del_case_url, headers=headers, timeout=TIMEOUT)
                assert del_case_resp.status_code == 200, f"Failed to delete case {case_id}"
            except Exception:
                pass
        if person_id:
            try:
                del_person_url = f"{BASE_URL}/api/v1/persons/{person_id}"
                del_person_resp = requests.delete(del_person_url, headers=headers, timeout=TIMEOUT)
                assert del_person_resp.status_code == 200, f"Failed to delete person {person_id}"
            except Exception:
                pass


test_upload_document_with_ocr_processing()
