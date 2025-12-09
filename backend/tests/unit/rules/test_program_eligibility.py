from datetime import date, timedelta

from src.app.domain_config.service import ConfigService
from src.app.rules.models import CandidateProfile, EducationRecord, LanguageTestResult, ProofOfFundsSnapshot, WorkExperienceRecord, JobOffer
from src.app.rules.program_eligibility import evaluate_programs


def _default_profile() -> CandidateProfile:
    today = date.today()
    return CandidateProfile(
        family_size=1,
        education=[EducationRecord(level="bachelor")],
        language_tests=[
            LanguageTestResult(
                test_type="IELTS",
                listening_clb=9,
                reading_clb=9,
                writing_clb=9,
                speaking_clb=9,
                expiry_date=today + timedelta(days=365),
            )
        ],
        proof_of_funds=[
            ProofOfFundsSnapshot(amount=20000, as_of_date=today),
        ],
        work_experience=[
            WorkExperienceRecord(
                teer_level=1,
                start_date=today - timedelta(days=365),
                end_date=today,
                is_continuous=True,
                is_canadian=False,
                is_paid=True,
            ),
        ],
    )


def test_fsw_happy_path() -> None:
    cfg = ConfigService().get_domain_rules()
    profile = _default_profile()

    summary = evaluate_programs(profile, cfg)
    fsw = next(r for r in summary.results if r.program_code == "FSW")

    assert fsw.eligible is True
    assert fsw.reasons == []


def test_fsw_language_failure() -> None:
    cfg = ConfigService().get_domain_rules()
    profile = _default_profile()
    profile.language_tests[0].listening_clb = 5
    profile.language_tests[0].reading_clb = 5
    profile.language_tests[0].writing_clb = 5
    profile.language_tests[0].speaking_clb = 5

    summary = evaluate_programs(profile, cfg)
    fsw = next(r for r in summary.results if r.program_code == "FSW")
    assert fsw.eligible is False
    assert any("CLB" in reason for reason in fsw.reasons)


def test_cec_happy_path() -> None:
    cfg = ConfigService().get_domain_rules()
    profile = _default_profile()
    today = date.today()
    # Replace with Canadian work
    profile.work_experience = [
        WorkExperienceRecord(
            teer_level=1,
            start_date=today - timedelta(days=365),
            end_date=today,
            is_continuous=True,
            is_canadian=True,
        )
    ]

    summary = evaluate_programs(profile, cfg)
    cec = next(r for r in summary.results if r.program_code == "CEC")
    assert cec.eligible is True


def test_fst_requires_job_offer() -> None:
    cfg = ConfigService().get_domain_rules()
    profile = _default_profile()
    summary = evaluate_programs(profile, cfg)
    fst = next(r for r in summary.results if r.program_code == "FST")
    assert fst.eligible is False
    assert any("job offer" in reason.lower() for reason in fst.reasons)

    # Add job offer to satisfy requirement
    profile.job_offers = [
        JobOffer(
            employer_name="ABC",
            noc_code="1234",
            teer_level=2,
            full_time=True,
            duration_months=12,
        )
    ]
    summary2 = evaluate_programs(profile, cfg)
    fst2 = next(r for r in summary2.results if r.program_code == "FST")
    # Language still high, so should now be eligible
    assert fst2.eligible is True


