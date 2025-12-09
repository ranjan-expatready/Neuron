import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.app.db.database import Base, SessionLocal, engine
from src.app.main import app
from src.app.models.tenant import Tenant

client = TestClient(app)


@pytest.fixture(scope="function")
def tenant_id() -> str:
    # Ensure schema is up to date for sqlite-backed SessionLocal
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        tenant = Tenant(name="Admin Config Tenant", plan_code="pro")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        yield tenant.id
    finally:
        db.close()


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


def test_get_full_domain_config(tenant_id: str):
    response = client.get("/api/v1/admin/config", params={"tenant_id": tenant_id})
    assert response.status_code == 200
    data = response.json()
    for key in EXPECTED_SECTIONS:
        assert key in data


def test_get_config_sections(tenant_id: str):
    response = client.get("/api/v1/admin/config/sections", params={"tenant_id": tenant_id})
    assert response.status_code == 200
    sections = response.json()
    for key in EXPECTED_SECTIONS:
        assert key in sections


def test_get_config_section_language(tenant_id: str):
    response = client.get("/api/v1/admin/config/language", params={"tenant_id": tenant_id})
    assert response.status_code == 200
    data = response.json()
    assert "fsw_min_clb" in data


def test_get_config_section_documents(tenant_id: str):
    response = client.get("/api/v1/admin/config/documents", params={"tenant_id": tenant_id})
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data


def test_get_config_section_forms(tenant_id: str):
    response = client.get("/api/v1/admin/config/forms", params={"tenant_id": tenant_id})
    assert response.status_code == 200
    data = response.json()
    assert "forms" in data


def test_get_config_section_not_found(tenant_id: str):
    response = client.get("/api/v1/admin/config/unknown_section", params={"tenant_id": tenant_id})
    assert response.status_code == 404
    assert "detail" in response.json()


def test_get_plans(tenant_id: str):
    response = client.get("/api/v1/admin/config/plans", params={"tenant_id": tenant_id})
    assert response.status_code == 200
    plans = response.json()
    assert any(plan["plan_code"] == "starter" for plan in plans)


def test_get_case_types(tenant_id: str):
    response = client.get("/api/v1/admin/config/case-types", params={"tenant_id": tenant_id})
    assert response.status_code == 200
    case_types = response.json()
    assert any(ct["code"] == "express_entry_basic" for ct in case_types)


