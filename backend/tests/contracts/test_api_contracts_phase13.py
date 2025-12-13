from src.app.services.submission_preparation import SubmissionPreparationPackage
from src.app.services.submission_readiness import DocumentReadinessItem, SubmissionReadinessResult
from src.app.services.submission_readiness_verification import EvidenceBundle, VerificationResult, VerificationVerdict


def test_submission_readiness_contract_schema():
    schema = SubmissionReadinessResult.model_json_schema()
    required = set(schema.get("required", []))
    expected_required = {"case_id", "tenant_id", "program_code", "status", "ready"}
    assert expected_required.issubset(required)
    props = schema["properties"]
    expected_props = expected_required | {
        "missing_documents",
        "documents",
        "blockers",
        "explanations",
        "engine_version",
        "evaluation_timestamp",
        "config_hash",
        "source_bundle_version",
    }
    for field in expected_props:
        assert field in props
    doc_schema = DocumentReadinessItem.model_json_schema()
    doc_props = set(doc_schema.get("properties", {}).keys())
    assert {"id", "label", "category", "required", "uploaded", "config_ref", "source_ref", "unsourced"}.issubset(
        doc_props
    )


def test_evidence_bundle_contract_schema():
    schema = EvidenceBundle.model_json_schema()
    props = set(schema.get("properties", {}).keys())
    expected_props = {
        "case_id",
        "tenant_id",
        "program_code",
        "engine_version",
        "verification_engine_version",
        "config_hashes",
        "consulted_configs",
        "readiness_result",
        "verification_result",
        "evidence_index",
        "bundle_version",
        "evaluation_timestamp",
        "source_bundle_version",
    }
    for field in expected_props:
        assert field in props
    verification_schema = VerificationResult.model_json_schema()
    assert "verdict" in verification_schema.get("required", [])
    allowed = {VerificationVerdict.PASS, VerificationVerdict.FAIL, VerificationVerdict.UNKNOWN}
    assert allowed == {"PASS", "FAIL", "UNKNOWN"}


def test_submission_preparation_contract_schema_includes_automation_gate():
    schema = SubmissionPreparationPackage.model_json_schema()
    props_dict = schema.get("properties", {})
    props = set(props_dict.keys())
    expected = {
        "package_version",
        "case_id",
        "tenant_id",
        "program_code",
        "engine_versions",
        "evaluation_timestamp",
        "forms",
        "gaps_summary",
        "readiness_reference",
        "audit",
        "automation_readiness",
        "deterministic_hash",
    }
    assert "automation_readiness" in props_dict
    auto_schema = props_dict["automation_readiness"]
    assert "$ref" in auto_schema or auto_schema.get("type") == "object"

