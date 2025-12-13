import pytest

from src.app.services.assisted_drafts import AssistedDraftService, AssistedDraftsError
from src.app.services.submission_preparation import (
    AutomationReadiness,
    GapsSummary,
    PreparationAttachment,
    PreparationField,
    PreparationForm,
    SubmissionPreparationPackage,
)


def _package(eligible: bool = True, blocking=None) -> SubmissionPreparationPackage:
    blocking = blocking or []
    auto = AutomationReadiness(
        automation_eligible=eligible,
        blocking_reasons=blocking,
        recommended_next_steps=[],
        engine_version="1.0.0",
        verification_verdict="PASS" if eligible else "FAIL",
        readiness_status="READY" if eligible else "NOT_READY",
        evidence_bundle_ref="ref",
    )
    form = PreparationForm(
        form_code="IMM0008",
        form_name="Generic App",
        fields=[
            PreparationField(
                field_code="given_name",
                source="canonical_profile",
                value_preview="John",
                status="mapped",
                notes=None,
            )
        ],
        attachments=[
            PreparationAttachment(doc_code="passport_main", status="available", evidence_ref="config/domain/documents"),
        ],
    )
    return SubmissionPreparationPackage(
        case_id="case-1",
        tenant_id="tenant-1",
        program_code="EE_FSW",
        engine_versions=["prep:1.0.0"],
        evaluation_timestamp="2025-12-13T12:00:00Z",
        forms=[form],
        gaps_summary=GapsSummary(blocking=blocking, non_blocking=[]),
        readiness_reference={"readiness_verdict": auto.verification_verdict, "evidence_bundle_ref": "ref"},
        audit={"config_hashes": ["hash"], "consulted_configs": ["documents.yaml"], "source_bundle_version": "v-source"},
        automation_readiness=auto,
        deterministic_hash="hash123",
    )


class FakePrepService:
    def __init__(self, pkg: SubmissionPreparationPackage):
        self.pkg = pkg

    def build_package(self, **kwargs):
        return self.pkg


def test_assisted_drafts_success(monkeypatch):
    pkg = _package(eligible=True, blocking=[])
    svc = AssistedDraftService(prep_service=FakePrepService(pkg))

    monkeypatch.setattr(
        "src.app.services.assisted_drafts.CaseRepository.get_case",
        lambda self, case_id, tenant_id, include_deleted=False: object(),
    )
    monkeypatch.setattr(
        AssistedDraftService,
        "_tenant_policy_enabled",
        lambda self, db_session, tenant_id: True,
    )

    bundle = svc.build_drafts(case_id="case-1", tenant_id="tenant-1", db_session=None, program_code="EE_FSW")
    assert bundle.is_draft is True
    assert bundle.drafts["checklist"].label.startswith("DRAFT")
    assert bundle.drafts["case_summary"].is_draft is True
    assert bundle.drafts["internal_review_notes"].is_draft is True
    assert bundle.automation_readiness_ref.automation_eligible is True


def test_assisted_drafts_policy_disabled(monkeypatch):
    pkg = _package(eligible=True, blocking=[])
    svc = AssistedDraftService(prep_service=FakePrepService(pkg))

    monkeypatch.setattr(
        "src.app.services.assisted_drafts.CaseRepository.get_case",
        lambda self, case_id, tenant_id, include_deleted=False: object(),
    )
    monkeypatch.setattr(
        AssistedDraftService,
        "_tenant_policy_enabled",
        lambda self, db_session, tenant_id: False,
    )

    with pytest.raises(AssistedDraftsError) as exc:
        svc.build_drafts(case_id="case-1", tenant_id="tenant-1", db_session=None, program_code="EE_FSW")
    assert exc.value.status_code == 403
    assert "disabled" in exc.value.reason


def test_assisted_drafts_not_eligible(monkeypatch):
    pkg = _package(eligible=False, blocking=["blocking_gap"])
    svc = AssistedDraftService(prep_service=FakePrepService(pkg))

    monkeypatch.setattr(
        "src.app.services.assisted_drafts.CaseRepository.get_case",
        lambda self, case_id, tenant_id, include_deleted=False: object(),
    )
    monkeypatch.setattr(
        AssistedDraftService,
        "_tenant_policy_enabled",
        lambda self, db_session, tenant_id: True,
    )

    with pytest.raises(AssistedDraftsError) as exc:
        svc.build_drafts(case_id="case-1", tenant_id="tenant-1", db_session=None, program_code="EE_FSW")
    assert exc.value.status_code == 412
    assert "blocking_gap" in exc.value.reason

