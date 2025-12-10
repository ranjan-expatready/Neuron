from fastapi.testclient import TestClient


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


def test_get_full_domain_config(client: TestClient, admin_headers):
    response = client.get("/api/v1/admin/config", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    for key in EXPECTED_SECTIONS:
        assert key in data


def test_get_config_sections(client: TestClient, admin_headers):
    response = client.get("/api/v1/admin/config/sections", headers=admin_headers)
    assert response.status_code == 200
    sections = response.json()
    for key in EXPECTED_SECTIONS:
        assert key in sections


def test_get_config_section_language(client: TestClient, admin_headers):
    response = client.get("/api/v1/admin/config/language", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "fsw_min_clb" in data


def test_get_config_section_documents(client: TestClient, admin_headers):
    response = client.get("/api/v1/admin/config/documents", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data


def test_get_config_section_forms(client: TestClient, admin_headers):
    response = client.get("/api/v1/admin/config/forms", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "forms" in data


def test_get_config_section_not_found(client: TestClient, admin_headers):
    response = client.get("/api/v1/admin/config/unknown_section", headers=admin_headers)
    assert response.status_code == 404
    assert "detail" in response.json()


