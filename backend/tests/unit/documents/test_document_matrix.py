from datetime import date

from src.app.documents.service import DocumentMatrixService
from src.app.domain_config.service import ConfigService
from src.app.rules.models import CandidateProfile, ProofOfFundsSnapshot


def _profile_single() -> CandidateProfile:
    return CandidateProfile(
        marital_status="single",
        family_size=1,
        proof_of_funds=[ProofOfFundsSnapshot(amount=20000, as_of_date=date.today())],
    )


def _profile_spouse() -> CandidateProfile:
    return CandidateProfile(
        marital_status="married",
        family_size=2,
        proof_of_funds=[ProofOfFundsSnapshot(amount=30000, as_of_date=date.today())],
    )


def test_fsw_single_requires_pof_and_core_forms() -> None:
    service = DocumentMatrixService(config_service=ConfigService())
    result = service.get_required_documents(_profile_single(), "fsw")

    assert "IMM0008" in result.required_forms
    assert any(d.id == "proof_of_funds" for d in result.required_documents)
    assert any(d.id == "passport" for d in result.required_documents)


def test_fsw_with_spouse_adds_spouse_form_and_doc() -> None:
    service = DocumentMatrixService(config_service=ConfigService())
    result = service.get_required_documents(_profile_spouse(), "fsw")

    assert "IMM5406" in result.required_forms
    assert any(d.id == "marriage_certificate" for d in result.required_documents)


def test_cec_has_no_pof_docs() -> None:
    service = DocumentMatrixService(config_service=ConfigService())
    result = service.get_required_documents(_profile_single(), "cec")

    assert not any(d.id == "proof_of_funds" for d in result.required_documents)


def test_fst_requires_trade_certificate() -> None:
    service = DocumentMatrixService(config_service=ConfigService())
    result = service.get_required_documents(_profile_single(), "fst")

    assert any(d.id == "trade_certificate" for d in result.required_documents)

