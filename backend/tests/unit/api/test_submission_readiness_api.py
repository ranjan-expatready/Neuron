import uuid

from fastapi.testclient import TestClient

from src.app.api.dependencies import get_current_user
from src.app.api.routes import forms_autofill
from src.app.config.form_config import clear_caches as clear_form_caches
from src.app.config.form_config import FormBundleDefinition
from src.app.domain.submission.models import (
    FormReadinessSummary,
    ReadinessCheckResult,
    ReadinessSeverity,
    SubmissionReadinessReport,
)
from src.app.models.user import User
from src.app.services.submission_readiness_service import SubmissionReadinessError, SubmissionReadinessService


def _dummy_report():
    return SubmissionReadinessReport(
        case_id="c1",
        bundle_id="bundle1",
        overall_status="READY",
        overall_completion_percent=100,
        blockers_count=0,
        warnings_count=0,
        forms=[
            FormReadinessSummary(
                form_id="FORM1",
                title="Form One",
                completion_percent=100,
                missing_required_fields=0,
                missing_required_documents=0,
                checks=[
                    ReadinessCheckResult(
                        code="ok",
                        severity=ReadinessSeverity.INFO,
                        message="all good",
                        form_id="FORM1",
                    )
                ],
            )
        ],
        missing_documents=[],
        notes=[],
    )


def test_submission_readiness_api_success(monkeypatch, client: TestClient, admin_headers):
    clear_form_caches()

    monkeypatch.setattr(SubmissionReadinessService, "generate_report", lambda self, **kwargs: _dummy_report())

    resp = client.get(
        f"/api/v1/cases/{uuid.uuid4()}/submission/readiness",
        params={"bundle_id": "bundle1"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_status"] == "READY"
    assert body["bundle_id"] == "bundle1"


def test_submission_readiness_api_invalid_bundle(monkeypatch, client: TestClient, admin_headers):
    clear_form_caches()

    def _raise_bundle(self, **kwargs):
        raise SubmissionReadinessError("Invalid bundle_id")

    monkeypatch.setattr(SubmissionReadinessService, "generate_report", _raise_bundle)

    resp = client.get(
        f"/api/v1/cases/{uuid.uuid4()}/submission/readiness",
        params={"bundle_id": "bad"},
        headers=admin_headers,
    )
    assert resp.status_code == 400
    assert "Invalid bundle_id" in resp.text


def test_submission_readiness_api_not_found(monkeypatch, client: TestClient, admin_headers):
    clear_form_caches()

    def _raise_not_found(self, **kwargs):
        raise SubmissionReadinessError("Case not found or tenant mismatch")

    monkeypatch.setattr(SubmissionReadinessService, "generate_report", _raise_not_found)

    resp = client.get(
        f"/api/v1/cases/{uuid.uuid4()}/submission/readiness",
        params={"bundle_id": "bundle1"},
        headers=admin_headers,
    )
    assert resp.status_code == 404


def test_submission_readiness_api_forbidden(monkeypatch, client: TestClient):
    clear_form_caches()

    def _client_user():
        return User(
            id=str(uuid.uuid4()),
            email="client@example.com",
            tenant_id=str(client.default_tenant.id),
            role="client",
        )

    client.app.dependency_overrides[get_current_user] = _client_user
    try:
        resp = client.get(f"/api/v1/cases/{uuid.uuid4()}/submission/readiness", params={"bundle_id": "bundle1"})
        assert resp.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)


def test_form_bundles_listing(monkeypatch, client: TestClient, admin_headers):
    clear_form_caches()
    bundles = [
        FormBundleDefinition(
            id="bundle1",
            label="Bundle 1",
            program_codes=["FSW"],
            forms=["FORM1"],
            status="active",
        )
    ]

    monkeypatch.setattr(forms_autofill, "load_form_bundles", lambda: bundles)

    resp = client.get("/api/v1/config/form-bundles", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body[0]["id"] == "bundle1"

