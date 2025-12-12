from src.app.cases.repository import CaseRepository
from src.app.config.form_config import clear_caches as clear_form_caches
from src.app.domain.forms.models import FormAutofillPreviewResult, FormAutofillResult, FormFieldAutofill
from src.app.domain.submission.models import ReadinessSeverity
from src.app.documents.service import DocumentItem, DocumentMatrixResult
from src.app.services.submission_readiness_service import SubmissionReadinessService


def _write_form_configs(tmp_path, required: bool = True):
    (tmp_path / "forms.yaml").write_text(
        """
form_definitions:
  - id: "FORM1"
    label: "Form One"
    version: "v1"
    status: "active"
    type: "pdf"
    fields:
      - field_id: "given_name"
        label: "Given"
        data_type: "text"
        required: %s
"""
        % ("true" if required else "false"),
        encoding="utf-8",
    )
    (tmp_path / "form_mappings.yaml").write_text(
        """
form_field_mappings:
  - id: "m1"
    form_id: "FORM1"
    field_id: "given_name"
    source_type: "canonical_profile"
    source_path: "profile.personal.given_name"
    status: "active"
""",
        encoding="utf-8",
    )
    (tmp_path / "form_bundles.yaml").write_text(
        """
form_bundles:
  - id: "bundle1"
    label: "Bundle 1"
    program_codes: ["FSW"]
    forms: ["FORM1"]
    status: "active"
""",
        encoding="utf-8",
    )


def _make_case(db_session, tenant_id: str, profile: dict):
    repo = CaseRepository(db_session)
    record = repo.create_case(
        profile=profile,
        program_eligibility={},
        crs_breakdown=None,
        required_artifacts=None,
        config_fingerprint={},
        source="test",
        status="active",
        tenant_id=tenant_id,
    )
    db_session.commit()
    return record


class _FakeAutofillEngine:
    def __init__(self, forms):
        self._forms = forms

    def build_autofill_preview(self, *, case_id, program_code, bundle_id, tenant_id, db_session):
        return FormAutofillPreviewResult(bundle_id=bundle_id, forms=self._forms, warnings=[])


class _FakeDocService:
    def __init__(self, required_docs=None):
        self._required_docs = required_docs or []

    def get_required_documents(self, profile, program_code):
        return DocumentMatrixResult(required_forms=[], required_documents=self._required_docs)


def test_submission_readiness_ready(tmp_path, client):
    clear_form_caches()
    _write_form_configs(tmp_path)
    tenant_id = str(client.default_tenant.id)
    case = _make_case(client.db_session, tenant_id, {"profile": {"personal": {"given_name": "John"}}})

    autofill = _FakeAutofillEngine(
        [
            FormAutofillResult(
                form_id="FORM1",
                fields=[
                    FormFieldAutofill(
                        form_id="FORM1",
                        field_id="given_name",
                        proposed_value="John",
                        source_type="canonical_profile",
                    )
                ],
            )
        ]
    )
    service = SubmissionReadinessService(
        base_path=str(tmp_path),
        autofill_engine=autofill,
        document_service=_FakeDocService([]),
    )

    report = service.generate_report(
        case_id=case.id, bundle_id="bundle1", tenant_id=tenant_id, db_session=client.db_session, program_code="FSW"
    )

    assert report.overall_status == "READY"
    assert report.blockers_count == 0
    assert report.warnings_count == 0
    assert report.overall_completion_percent == 100


def test_submission_readiness_missing_required_field(tmp_path, client):
    clear_form_caches()
    _write_form_configs(tmp_path)
    tenant_id = str(client.default_tenant.id)
    case = _make_case(client.db_session, tenant_id, {"profile": {"personal": {}}})

    autofill = _FakeAutofillEngine(
        [
            FormAutofillResult(
                form_id="FORM1",
                fields=[
                    FormFieldAutofill(
                        form_id="FORM1",
                        field_id="given_name",
                        proposed_value=None,
                        source_type="canonical_profile",
                        notes="missing canonical data",
                    )
                ],
            )
        ]
    )
    service = SubmissionReadinessService(
        base_path=str(tmp_path),
        autofill_engine=autofill,
        document_service=_FakeDocService([]),
    )

    report = service.generate_report(
        case_id=case.id, bundle_id="bundle1", tenant_id=tenant_id, db_session=client.db_session, program_code="FSW"
    )

    assert report.overall_status == "NOT_READY"
    assert report.blockers_count == 1
    assert report.forms[0].missing_required_fields == 1


def test_submission_readiness_warns_on_notes(tmp_path, client):
    clear_form_caches()
    _write_form_configs(tmp_path)
    tenant_id = str(client.default_tenant.id)
    case = _make_case(client.db_session, tenant_id, {"profile": {"personal": {"given_name": "John"}}})

    autofill = _FakeAutofillEngine(
        [
            FormAutofillResult(
                form_id="FORM1",
                fields=[
                    FormFieldAutofill(
                        form_id="FORM1",
                        field_id="given_name",
                        proposed_value="John",
                        source_type="canonical_profile",
                        notes="inferred from partial data",
                    )
                ],
            )
        ]
    )
    service = SubmissionReadinessService(
        base_path=str(tmp_path),
        autofill_engine=autofill,
        document_service=_FakeDocService([]),
    )

    report = service.generate_report(
        case_id=case.id, bundle_id="bundle1", tenant_id=tenant_id, db_session=client.db_session, program_code="FSW"
    )

    assert report.overall_status == "NEEDS_REVIEW"
    assert report.warnings_count == 1
    assert report.blockers_count == 0
    assert any(c.severity == ReadinessSeverity.WARN for c in report.forms[0].checks)


def test_submission_readiness_missing_required_document(tmp_path, client):
    clear_form_caches()
    _write_form_configs(tmp_path)
    tenant_id = str(client.default_tenant.id)
    case = _make_case(client.db_session, tenant_id, {"profile": {"personal": {"given_name": "John"}}})

    required_docs = [DocumentItem(id="passport", label="Passport", category="identity", mandatory=True)]
    autofill = _FakeAutofillEngine(
        [
            FormAutofillResult(
                form_id="FORM1",
                fields=[
                    FormFieldAutofill(
                        form_id="FORM1",
                        field_id="given_name",
                        proposed_value="John",
                        source_type="canonical_profile",
                    )
                ],
            )
        ]
    )
    service = SubmissionReadinessService(
        base_path=str(tmp_path),
        autofill_engine=autofill,
        document_service=_FakeDocService(required_docs),
    )

    report = service.generate_report(
        case_id=case.id, bundle_id="bundle1", tenant_id=tenant_id, db_session=client.db_session, program_code="FSW"
    )

    assert report.overall_status == "NOT_READY"
    assert "passport" in report.missing_documents
    assert report.forms[0].missing_required_documents == 1
    assert any(c.code == "missing_required_document" for c in report.forms[0].checks)

