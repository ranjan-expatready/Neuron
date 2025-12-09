from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


EXPECTED_SECTIONS = [
    "crs_core",
    "crs_transferability",
    "language",
    "clb_tables",
    "work_experience",
    "proof_of_funds",
    "program_rules",
    "arranged_employment",
    "biometrics_medicals",
    "documents",
    "forms",
]


def test_get_full_domain_config():
    response = client.get("/api/v1/admin/config")
    assert response.status_code == 200
    data = response.json()
    for key in EXPECTED_SECTIONS:
        assert key in data


def test_get_config_sections():
    response = client.get("/api/v1/admin/config/sections")
    assert response.status_code == 200
    sections = response.json()
    for key in EXPECTED_SECTIONS:
        assert key in sections


def test_get_config_section_language():
    response = client.get("/api/v1/admin/config/language")
    assert response.status_code == 200
    data = response.json()
    assert "fsw_min_clb" in data


def test_get_config_section_documents():
    response = client.get("/api/v1/admin/config/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data


def test_get_config_section_forms():
    response = client.get("/api/v1/admin/config/forms")
    assert response.status_code == 200
    data = response.json()
    assert "forms" in data


def test_get_config_section_not_found():
    response = client.get("/api/v1/admin/config/unknown_section")
    assert response.status_code == 404
    assert "detail" in response.json()



