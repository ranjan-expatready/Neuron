from datetime import datetime

from src.app.domain.forms.models import FormAutofillPreviewResult, FormAutofillResult, FormFieldAutofill
from src.app.services.submission_preparation import SubmissionPreparationService, PreparationAttachment
from src.app.services.submission_readiness import SubmissionReadinessResult, DocumentReadinessItem, Blocker
from src.app.services.submission_readiness_verification import EvidenceBundle, VerificationResult


class FakeReadinessService:
    def __init__(self, readiness: SubmissionReadinessResult, verification_verdict: str = "PASS") -> None:
        self.readiness = readiness
        self.verification_verdict = verification_verdict

    def build_evidence_bundle(self, *, case_id: str, tenant_id: str, program_code: str | None, db_session):
        return EvidenceBundle(
            case_id=case_id,
            tenant_id=tenant_id,
            program_code=program_code or self.readiness.program_code,
            engine_version=self.readiness.engine_version,
            verification_engine_version="1.0.0",
            evaluation_timestamp="2025-12-13T12:00:00Z",
            config_hashes=["hash-config"],
            consulted_configs=["documents.yaml"],
            source_bundle_version=self.readiness.source_bundle_version,
            readiness_result=self.readiness,
            verification_result=VerificationResult(verdict=self.verification_verdict, reasons=[], warnings=[]),
            evidence_index=["config/domain/documents.yaml#passport_main"],
        )


class FakeFormEngine:
    def __init__(self, preview: FormAutofillPreviewResult) -> None:
        self.preview = preview

    def build_autofill_preview(self, *, case_id: str, program_code: str | None, tenant_id: str, db_session):
        return self.preview


def _base_readiness(status: str = "READY", missing=None, blockers=None):
    missing = missing or []
    blockers = blockers or []
    return SubmissionReadinessResult(
        case_id="case-1",
        tenant_id="tenant-1",
        program_code="EE_FSW",
        status=status,
        ready=status == "READY",
        missing_documents=missing,
        documents=[
            DocumentReadinessItem(
                id="passport_main",
                label="Passport – main applicant",
                category="identity",
                required=True,
                reasons=[],
                uploaded="passport_main" not in missing,
                matched_document_ids=[],
                config_ref="config/domain/documents.yaml#passport_main",
                source_ref="domain_knowledge/passport",
                unsourced=False,
            )
        ],
        blockers=blockers,
        explanations=[],
        engine_version="1.0.0",
        evaluation_timestamp="2025-12-13T12:00:00Z",
        config_hash="abc",
        source_bundle_version="v-source",
    )


def _preview(field_value):
    return FormAutofillPreviewResult(
        bundle_id="bundle",
        forms=[
            FormAutofillResult(
                form_id="IMM0008",
                fields=[
                    FormFieldAutofill(
                        form_id="IMM0008",
                        field_id="given_name",
                        proposed_value=field_value,
                        source_type="canonical_profile",
                        source_path="profile.personal.given_name",
                        notes=None if field_value else "missing canonical data",
                        conflicts=[],
                    )
                ],
                warnings=[],
            )
        ],
        warnings=[],
    )


def test_complete_package_no_blocking_gaps():
    readiness = _base_readiness(status="READY", missing=[])
    svc = SubmissionPreparationService(
        readiness_service=FakeReadinessService(readiness, verification_verdict="PASS"),
        form_engine=FakeFormEngine(_preview("John")),
    )

    pkg = svc.build_package(case_id="case-1", tenant_id="tenant-1", program_code="EE_FSW", db_session=None)

    assert pkg.gaps_summary.blocking == []
    assert pkg.readiness_reference["readiness_verdict"] == "PASS"
    assert pkg.forms[0].fields[0].status == "mapped"
    assert pkg.deterministic_hash


def test_missing_field_creates_blocking_gap():
    readiness = _base_readiness(status="NOT_READY", missing=[])
    svc = SubmissionPreparationService(
        readiness_service=FakeReadinessService(readiness, verification_verdict="FAIL"),
        form_engine=FakeFormEngine(_preview(None)),
    )

    pkg = svc.build_package(case_id="case-2", tenant_id="tenant-1", program_code="EE_FSW", db_session=None)
    assert "field:IMM0008:given_name" in pkg.gaps_summary.blocking
    assert pkg.readiness_reference["readiness_verdict"] == "FAIL"


def test_missing_attachment_creates_blocking_gap():
    readiness = _base_readiness(status="NOT_READY", missing=["passport_main"])
    svc = SubmissionPreparationService(
        readiness_service=FakeReadinessService(readiness, verification_verdict="FAIL"),
        form_engine=FakeFormEngine(_preview("John")),
    )

    pkg = svc.build_package(case_id="case-3", tenant_id="tenant-1", program_code="EE_FSW", db_session=None)
    assert any(gap.startswith("attachment:IMM0008:passport_main") for gap in pkg.gaps_summary.blocking)


def test_unknown_readiness_propagates_verdict():
    readiness = _base_readiness(status="UNKNOWN", missing=[])
    svc = SubmissionPreparationService(
        readiness_service=FakeReadinessService(readiness, verification_verdict="UNKNOWN"),
        form_engine=FakeFormEngine(_preview("John")),
    )

    pkg = svc.build_package(case_id="case-4", tenant_id="tenant-1", program_code="EE_FSW", db_session=None)
    assert pkg.readiness_reference["readiness_verdict"] == "UNKNOWN"


def test_deterministic_hash_stable():
    readiness = _base_readiness(status="READY", missing=[])
    svc = SubmissionPreparationService(
        readiness_service=FakeReadinessService(readiness, verification_verdict="PASS"),
        form_engine=FakeFormEngine(_preview("John")),
    )

    pkg1 = svc.build_package(case_id="case-5", tenant_id="tenant-1", program_code="EE_FSW", db_session=None)
    pkg2 = svc.build_package(case_id="case-5", tenant_id="tenant-1", program_code="EE_FSW", db_session=None)
    assert pkg1.deterministic_hash == pkg2.deterministic_hash


