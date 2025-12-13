import json
import uuid

import pytest

from src.app.cases.repository import CaseRepository
from src.app.models.document import Document
from src.app.services.submission_readiness_verification import (
    SubmissionReadinessVerificationService,
    VerificationVerdict,
)
from src.app.config.intake_config import clear_intake_config_cache


def _write_minimal_bundle(base_path, include_source=True):
    source_ref = "domain_knowledge/passport.md#identity" if include_source else None
    doc_block = []
    doc_block.append('    config_ref: "config/domain/documents.yaml#passport"')
    if source_ref:
        doc_block.append(f'    source_ref: "{source_ref}"')
    doc_extra = "\n".join(doc_block)
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
        f"""
document_definitions:
  - id: "passport"
    label: "Passport"
    category: "identity"
    required_for_programs: ["EE_FSW"]
    required_when: []
{doc_extra}
""",
        encoding="utf-8",
    )
    (base_path / "forms.yaml").write_text("form_definitions: []\n", encoding="utf-8")
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


def _baseline_bundle(tmp_path, client, include_source=True):
    _write_minimal_bundle(tmp_path, include_source=include_source)
    org_id = str(client.default_org.id)
    user_id = str(client.default_user.id)
    case_id = _make_case(
        client.db_session,
        org_id,
        {"profile": {"personal": {"marital_status": "single"}}},
    )
    if include_source:
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
    return case_id, org_id


def test_evidence_bundle_pass(tmp_path, client):
    case_id, org_id = _baseline_bundle(tmp_path, client, include_source=True)
    svc = SubmissionReadinessVerificationService(base_path=str(tmp_path))
    bundle = svc.build_evidence_bundle(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    )
    assert bundle.verification_result.verdict == VerificationVerdict.PASS
    assert "config/domain/documents.yaml#passport" in bundle.evidence_index
    assert "domain_knowledge/passport.md#identity" in bundle.evidence_index
    b1 = bundle.model_dump()
    b1.pop("evaluation_timestamp", None)
    b1["readiness_result"].pop("evaluation_timestamp", None)
    b2 = svc.build_evidence_bundle(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    ).model_dump()
    b2.pop("evaluation_timestamp", None)
    b2["readiness_result"].pop("evaluation_timestamp", None)
    assert b1 == b2


def test_evidence_bundle_fail_missing_source(tmp_path, client):
    case_id, org_id = _baseline_bundle(tmp_path, client, include_source=False)
    svc = SubmissionReadinessVerificationService(base_path=str(tmp_path))
    bundle = svc.build_evidence_bundle(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    )
    assert bundle.verification_result.verdict == VerificationVerdict.FAIL
    assert any("unsourced_requirement" in r for r in bundle.verification_result.reasons)


def test_evidence_bundle_unknown_on_ambiguous_program(tmp_path, client):
    _write_minimal_bundle(tmp_path, include_source=True)
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
    svc = SubmissionReadinessVerificationService(base_path=str(tmp_path))
    bundle = svc.build_evidence_bundle(
        case_id=case_id,
        tenant_id=org_id,
        program_code=None,
        db_session=client.db_session,
    )
    assert bundle.verification_result.verdict == VerificationVerdict.UNKNOWN
    assert "status_unknown" in bundle.verification_result.reasons


def test_bundle_schema_stability(tmp_path, client):
    case_id, org_id = _baseline_bundle(tmp_path, client, include_source=True)
    svc = SubmissionReadinessVerificationService(base_path=str(tmp_path))
    bundle = svc.build_evidence_bundle(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    )
    dumped = json.loads(bundle.model_dump_json())
    assert dumped["bundle_version"] == "v1"
    assert "readiness_result" in dumped
    assert "verification_result" in dumped
    assert isinstance(dumped["evidence_index"], list)
import json
import uuid

import pytest

from src.app.cases.repository import CaseRepository
from src.app.models.document import Document
from src.app.services.submission_readiness_verification import (
    SubmissionReadinessVerificationService,
    VerificationVerdict,
)
from src.app.services.submission_readiness import SubmissionReadinessEngineError
from src.app.config.intake_config import clear_intake_config_cache


def _write_minimal_intake_bundle(base_path, include_source=True):
    source_ref = "domain_knowledge/passport.md#identity" if include_source else None
    config_ref = "config/domain/documents.yaml#passport"
    doc_block = f"    source_ref: \"{source_ref}\"" if include_source else ""
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
        f"""
document_definitions:
  - id: "passport"
    label: "Passport"
    category: "identity"
    required_for_programs: ["EE_FSW"]
    required_when: []
    config_ref: "{config_ref}"
{doc_block}
""",
        encoding="utf-8",
    )
    (base_path / "forms.yaml").write_text("form_definitions: []\n", encoding="utf-8")
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


def _baseline_bundle(tmp_path, client, include_source=True):
    _write_minimal_intake_bundle(tmp_path, include_source=include_source)
    org_id = str(client.default_org.id)
    user_id = str(client.default_user.id)
    case_id = _make_case(
        client.db_session,
        org_id,
        {"profile": {"personal": {"marital_status": "single"}}},
    )
    if include_source:
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
    return case_id, org_id


def test_evidence_bundle_pass(tmp_path, client):
    case_id, org_id = _baseline_bundle(tmp_path, client, include_source=True)
    svc = SubmissionReadinessVerificationService(base_path=str(tmp_path))
    bundle = svc.build_evidence_bundle(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    )
    assert bundle.verification_result.verdict == VerificationVerdict.PASS
    assert "all" not in bundle.verification_result.reasons
    assert bundle.readiness_result.ready is True
    assert "config/domain/documents.yaml#passport" in bundle.evidence_index
    assert "domain_knowledge/passport.md#identity" in bundle.evidence_index
    # determinism ignoring timestamp
    b1 = bundle.model_dump()
    b1.pop("evaluation_timestamp", None)
    b1["readiness_result"].pop("evaluation_timestamp", None)
    b2 = svc.build_evidence_bundle(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    ).model_dump()
    b2.pop("evaluation_timestamp", None)
    b2["readiness_result"].pop("evaluation_timestamp", None)
    assert b1 == b2


def test_evidence_bundle_fail_unsourced(tmp_path, client):
    case_id, org_id = _baseline_bundle(tmp_path, client, include_source=False)
    svc = SubmissionReadinessVerificationService(base_path=str(tmp_path))
    bundle = svc.build_evidence_bundle(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    )
    assert bundle.verification_result.verdict == VerificationVerdict.FAIL
    assert any("unsourced" in r for r in bundle.verification_result.reasons)


def test_evidence_bundle_unknown_on_ambiguous_program(tmp_path, client):
    _write_minimal_intake_bundle(tmp_path, include_source=True)
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
    svc = SubmissionReadinessVerificationService(base_path=str(tmp_path))
    bundle = svc.build_evidence_bundle(
        case_id=case_id,
        tenant_id=org_id,
        program_code=None,
        db_session=client.db_session,
    )
    assert bundle.verification_result.verdict == VerificationVerdict.UNKNOWN
    assert "status_unknown" in bundle.verification_result.reasons


def test_bundle_schema_stability(tmp_path, client):
    case_id, org_id = _baseline_bundle(tmp_path, client, include_source=True)
    svc = SubmissionReadinessVerificationService(base_path=str(tmp_path))
    bundle = svc.build_evidence_bundle(
        case_id=case_id,
        tenant_id=org_id,
        program_code="EE_FSW",
        db_session=client.db_session,
    )
    dumped = json.loads(bundle.model_dump_json())
    assert dumped["bundle_version"] == "v1"
    assert "readiness_result" in dumped
    assert "verification_result" in dumped
    assert isinstance(dumped["evidence_index"], list)

