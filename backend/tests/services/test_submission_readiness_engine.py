import uuid

import pytest

from src.app.cases.repository import CaseRepository
from src.app.models.document import Document
from src.app.services.submission_readiness import (
    SubmissionReadinessEngine,
    SubmissionReadinessEngineError,
)
from src.app.config.intake_config import clear_intake_config_cache


def _write_minimal_intake_bundle(base_path):
    (base_path / "fields.yaml").write_text(
        """
fields:
  - id: "marital_status"
    label: "Marital Status"
    data_path: "profile.personal.marital_status"
    type: "string"
    required: true
""",
        encoding="utf-8",
    )
    (base_path / "intake_templates.yaml").write_text(
        """
intake_templates:
  - id: "tpl1"
    label: "EE FSW"
    applicable_programs: ["EE_FSW"]
    steps:
      - id: "s1"
        label: "Basics"
        fields: ["marital_status"]
""",
        encoding="utf-8",
    )
    (base_path / "documents.yaml").write_text(
        """
document_definitions:
  - id: "passport"
    label: "Passport"
    category: "identity"
    required_for_programs: ["EE_FSW"]
    required_when: []
    config_ref: "config/domain/documents.yaml#passport"
    source_ref: "domain_knowledge/passport.md#identity"
  - id: "unsourced_doc"
    label: "UnSourced"
    category: "other"
    required_for_programs: ["EE_FSW"]
    required_when: []
""",
        encoding="utf-8",
    )
    (base_path / "forms.yaml").write_text(
        """
form_definitions: []
""",
        encoding="utf-8",
    )
    clear_intake_config_cache()


def _make_case(db_session, org_id: str, profile: dict, program_results=None) -> str:
    repo = CaseRepository(db_session)
    record = repo.create_case(
        profile=profile,
        program_eligibility=program_results
        if program_results is not None
        else {"results": [{"program_code": "EE_FSW", "eligible": True}]},
        crs_breakdown=None,
        required_artifacts=None,
        config_fingerprint={},
        source="test",
        status="active",
        tenant_id=org_id,
    )
    db_session.commit()
    return str(record.id)


def test_submission_readiness_marks_missing_documents(tmp_path, client):
    _write_minimal_intake_bundle(tmp_path)
    org_id = str(client.default_org.id)
    case_id = _make_case(
        client.db_session,
        org_id,
        {"profile": {"personal": {"marital_status": "single"}}},
    )

    engine = SubmissionReadinessEngine(base_path=str(tmp_path))
    result = engine.evaluate_case(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    )

    assert result.ready is False
    assert "passport" in result.missing_documents


def test_submission_readiness_ready_when_required_doc_uploaded(tmp_path, client):
    _write_minimal_intake_bundle(tmp_path)
    org_id = str(client.default_org.id)
    user_id = str(client.default_user.id)
    case_id = _make_case(
        client.db_session,
        org_id,
        {"profile": {"personal": {"marital_status": "single"}}},
    )

    doc = Document(
        id=str(uuid.uuid4()),
        org_id=org_id,
        case_id=case_id,
        person_id=None,
        document_type="passport",
        category="identity",
        title="Passport Scan",
        description="",
        filename="passport.pdf",
        original_filename="passport.pdf",
        file_size=123,
        mime_type="application/pdf",
        storage_key="org/case/passport.pdf",
        storage_provider="local",
        processing_status="completed",
        ocr_status="pending",
        validation_status="pending",
        access_level="case_team",
        uploaded_by=user_id,
    )
    client.db_session.add(doc)
    client.db_session.commit()

    engine = SubmissionReadinessEngine(base_path=str(tmp_path))
    first = engine.evaluate_case(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    )
    second = engine.evaluate_case(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    )

    assert first.ready is True
    assert first.missing_documents == []
    passport_item = next(item for item in first.documents if item.id == "passport")
    assert passport_item.uploaded is True
    assert doc.id in passport_item.matched_document_ids
    # deterministic ordering and metadata except timestamp
    f_dump = first.model_dump()
    s_dump = second.model_dump()
    f_dump.pop("evaluation_timestamp", None)
    s_dump.pop("evaluation_timestamp", None)
    assert f_dump == s_dump


def test_submission_readiness_requires_program(client):
    org_id = str(client.default_org.id)
    case_id = _make_case(
        client.db_session,
        org_id,
        {"profile": {"personal": {"marital_status": "single"}}},
        program_results={},
    )

    engine = SubmissionReadinessEngine()
    with pytest.raises(SubmissionReadinessEngineError):
        engine.evaluate_case(
            case_id=case_id,
            tenant_id=org_id,
            program_code=None,
            db_session=client.db_session,
        )


def test_ambiguous_program_inference_returns_error(tmp_path, client):
    _write_minimal_intake_bundle(tmp_path)
    org_id = str(client.default_org.id)
    case_id = _make_case(
        client.db_session,
        org_id,
        {"profile": {"personal": {"marital_status": "single"}}},
        program_results={
            "results": [
                {"program_code": "EE_FSW", "eligible": True},
                {"program_code": "EE_FST", "eligible": True},
            ]
        },
    )

    engine = SubmissionReadinessEngine(base_path=str(tmp_path))
    with pytest.raises(SubmissionReadinessEngineError):
        engine.evaluate_case(
            case_id=case_id,
            tenant_id=org_id,
            program_code=None,
            db_session=client.db_session,
        )


def test_unsourced_requirements_do_not_block(tmp_path, client):
    _write_minimal_intake_bundle(tmp_path)
    org_id = str(client.default_org.id)
    user_id = str(client.default_user.id)
    case_id = _make_case(
        client.db_session,
        org_id,
        {"profile": {"personal": {"marital_status": "single"}}},
    )

    # Upload passport only (sourced). Unsourced item should not block readiness.
    doc = Document(
        id=str(uuid.uuid4()),
        org_id=org_id,
        case_id=case_id,
        person_id=None,
        document_type="passport",
        category="identity",
        title="Passport Scan",
        description="",
        filename="passport.pdf",
        original_filename="passport.pdf",
        file_size=123,
        mime_type="application/pdf",
        storage_key="org/case/passport.pdf",
        storage_provider="local",
        processing_status="completed",
        ocr_status="pending",
        validation_status="pending",
        access_level="case_team",
        uploaded_by=user_id,
    )
    client.db_session.add(doc)
    client.db_session.commit()

    engine = SubmissionReadinessEngine(base_path=str(tmp_path))
    result = engine.evaluate_case(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    )

    assert result.ready is True
    assert "unsourced_doc" not in result.missing_documents
    unsourced = next(item for item in result.documents if item.id == "unsourced_doc")
    assert unsourced.unsourced is True
    assert unsourced.source_ref == "UNSOURCED"
    assert "UNSOURCED requirement: unsourced_doc" in result.explanations


def test_config_hash_changes_with_config(tmp_path, client):
    # baseline bundle
    _write_minimal_intake_bundle(tmp_path)
    org_id = str(client.default_org.id)
    case_id = _make_case(
        client.db_session,
        org_id,
        {"profile": {"personal": {"marital_status": "single"}}},
    )
    engine = SubmissionReadinessEngine(base_path=str(tmp_path))
    baseline = engine.evaluate_case(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    )

    # modify config in new base path
    new_base = tmp_path / "alt"
    new_base.mkdir()
    _write_minimal_intake_bundle(new_base)
    # tweak document label so hash changes
    docs = (new_base / "documents.yaml").read_text(encoding="utf-8")
    (new_base / "documents.yaml").write_text(docs.replace("Passport", "Passport Doc"), encoding="utf-8")
    clear_intake_config_cache()

    engine_alt = SubmissionReadinessEngine(base_path=str(new_base))
    alt = engine_alt.evaluate_case(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    )

    assert baseline.config_hash != alt.config_hash

