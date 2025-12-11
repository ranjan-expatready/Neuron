import pytest
from sqlalchemy.orm import Session

from src.app.cases.models_db import CaseRecord
from src.app.cases.repository import CaseRepository
from src.app.domain.forms.models import FormAutofillPreviewResult
from src.app.services.form_autofill_engine import FormAutofillEngine, FormAutofillEngineError


def _make_case(db_session: Session, org_id: str, profile: dict) -> CaseRecord:
    repo = CaseRepository(db_session)
    record = repo.create_case(
        profile=profile,
        program_eligibility={},
        crs_breakdown=None,
        required_artifacts=None,
        config_fingerprint={},
        source="test",
        status="active",
        tenant_id=org_id,
    )
    db_session.commit()
    return record


def test_autofill_happy_path_uses_canonical_profile(client):
    org_id = str(client.default_org.id)
    profile = {
        "profile": {
            "personal": {
                "given_name": "John",
                "family_name": "Doe",
                "date_of_birth": "1990-01-01",
                "marital_status": "single",
            }
        }
    }
    case = _make_case(client.db_session, org_id, profile)

    engine = FormAutofillEngine()
    result = engine.build_autofill_preview(
        case_id=case.id,
        program_code="EE_FSW",
        tenant_id=org_id,
        db_session=client.db_session,
    )

    assert isinstance(result, FormAutofillPreviewResult)
    imm0008 = next(f for f in result.forms if f.form_id == "IMM0008")
    field_map = {f.field_id: f.proposed_value for f in imm0008.fields}
    assert field_map["given_name"] == "John"
    assert field_map["family_name"] == "Doe"
    assert result.bundle_id in {None, "ee_fsw_base_package"}


def test_autofill_missing_data_adds_notes(client):
    org_id = str(client.default_org.id)
    profile = {"profile": {"personal": {"given_name": "Jane"}}}
    case = _make_case(client.db_session, org_id, profile)

    engine = FormAutofillEngine()
    result = engine.build_autofill_preview(
        case_id=case.id,
        program_code="EE_FSW",
        tenant_id=org_id,
        db_session=client.db_session,
    )
    imm0008 = next(f for f in result.forms if f.form_id == "IMM0008")
    marital = next(f for f in imm0008.fields if f.field_id == "marital_status")
    assert marital.proposed_value is None
    assert "missing canonical data" in (marital.notes or "")


def test_bundle_without_form_definition_warns(tmp_path, client):
    base = tmp_path
    (base / "forms.yaml").write_text(
        """
form_definitions:
  - id: "FORM1"
    label: "Form1"
    version: "v1"
    status: "active"
    type: "pdf"
    fields:
      - field_id: "a"
        label: "A"
        data_type: "text"
        required: true
""",
        encoding="utf-8",
    )
    (base / "form_mappings.yaml").write_text(
        """
form_field_mappings:
  - id: "m1"
    form_id: "FORM1"
    field_id: "a"
    source_type: "canonical_profile"
    source_path: "profile.a"
    status: "active"
""",
        encoding="utf-8",
    )
    (base / "form_bundles.yaml").write_text(
        """
form_bundles:
  - id: "bundle1"
    label: "bundle"
    program_codes: ["EE_FSW"]
    forms: ["UNKNOWN_FORM"]
    status: "active"
""",
        encoding="utf-8",
    )

    org_id = str(client.default_org.id)
    case = _make_case(client.db_session, org_id, {"profile": {"a": "x"}})

    engine = FormAutofillEngine(base_path=str(base))
    result = engine.build_autofill_preview(
        case_id=case.id,
        program_code="EE_FSW",
        tenant_id=org_id,
        db_session=client.db_session,
    )
    assert any("UNKNOWN_FORM" in w for w in result.warnings)


def test_unknown_source_type_raises(tmp_path, client):
    base = tmp_path
    (base / "forms.yaml").write_text(
        """
form_definitions:
  - id: "F1"
    label: "Form1"
    version: "v1"
    status: "active"
    type: "pdf"
    fields:
      - field_id: "a"
        label: "A"
        data_type: "text"
        required: true
""",
        encoding="utf-8",
    )
    (base / "form_mappings.yaml").write_text(
        """
form_field_mappings:
  - id: "m1"
    form_id: "F1"
    field_id: "a"
    source_type: "unsupported"
    source_path: "profile.a"
    status: "active"
""",
        encoding="utf-8",
    )
    (base / "form_bundles.yaml").write_text(
        """
form_bundles:
  - id: "bundle1"
    label: "bundle"
    program_codes: ["EE_FSW"]
    forms: ["F1"]
    status: "active"
""",
        encoding="utf-8",
    )

    org_id = str(client.default_org.id)
    case = _make_case(client.db_session, org_id, {"profile": {"a": "x"}})

    engine = FormAutofillEngine(base_path=str(base))
    with pytest.raises(FormAutofillEngineError):
        engine.build_autofill_preview(
            case_id=case.id,
            program_code="EE_FSW",
            tenant_id=org_id,
            db_session=client.db_session,
        )

