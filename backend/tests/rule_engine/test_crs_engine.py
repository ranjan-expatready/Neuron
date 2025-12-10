from datetime import date

from src.app.domain.crs.models import (
    CRSProfileInput,
    EducationLevel,
    LanguageCLBProfile,
    MaritalStatus,
)
from src.app.domain_config.service import ConfigService
from src.app.rules.crs_adapter import build_crs_profile_from_candidate
from src.app.rules.models import (
    CandidateProfile,
    EducationRecord,
    LanguageTestResult,
    WorkExperienceRecord,
)
from src.app.services.crs_engine import CRSEngineService


def _assert_explanations_present(result):
    for contrib in result.factor_contributions:
        assert contrib.explanation is not None
        assert contrib.explanation.explanation_code
        assert contrib.explanation.rule_path
        assert isinstance(contrib.explanation.input_summary, dict)
        assert isinstance(contrib.explanation.threshold_summary, dict)


def test_single_applicant_clb9_bachelor_foreign_work():
    service = CRSEngineService()
    profile = CRSProfileInput(
        age=29,
        marital_status=MaritalStatus.SINGLE,
        education_level=EducationLevel.BACHELOR_THREE_YEAR_PLUS,
        first_official_language=LanguageCLBProfile(
            reading=9, writing=9, listening=9, speaking=9
        ),
        canadian_work_experience_years=0,
        foreign_work_experience_years=3,
    )

    result = service.compute_for_profile(profile)

    assert result.total_score == 429  # Derived from config/domain/crs.yaml tables
    assert any(c.factor_code == "core_human_capital_age" for c in result.factor_contributions)
    assert any(c.factor_code == "transferability_foreign_work_language" for c in result.factor_contributions)
    _assert_explanations_present(result)


def test_married_applicant_with_spouse_factors():
    service = CRSEngineService()
    profile = CRSProfileInput(
        age=29,
        marital_status=MaritalStatus.MARRIED,
        education_level=EducationLevel.BACHELOR_THREE_YEAR_PLUS,
        first_official_language=LanguageCLBProfile(
            reading=9, writing=9, listening=9, speaking=9
        ),
        canadian_work_experience_years=1,
        foreign_work_experience_years=1,
        spouse_education_level=EducationLevel.SECONDARY,
        spouse_language=LanguageCLBProfile(reading=7, writing=7, listening=7, speaking=7),
        spouse_canadian_work_experience_years=1,
    )

    result = service.compute_for_profile(profile)

    assert result.total_score == 458
    spouse_codes = {c.factor_code for c in result.factor_contributions}
    assert "spouse_education" in spouse_codes
    assert "spouse_language" in spouse_codes
    _assert_explanations_present(result)


def test_second_language_points_capped_at_config():
    service = CRSEngineService()
    cfg = ConfigService().get_domain_rules()
    profile = CRSProfileInput(
        age=30,
        marital_status=MaritalStatus.SINGLE,
        education_level=EducationLevel.BACHELOR_THREE_YEAR_PLUS,
        first_official_language=LanguageCLBProfile(reading=10, writing=10, listening=10, speaking=10),
        second_official_language=LanguageCLBProfile(reading=10, writing=10, listening=10, speaking=10),
        canadian_work_experience_years=0,
        foreign_work_experience_years=0,
    )

    result = service.compute_for_profile(profile)

    second_lang = next(
        c for c in result.factor_contributions if c.factor_code == "core_human_capital_second_official_language"
    )
    expected_cap = cfg.crs_core.second_official_language.max_points_single
    assert second_lang.points_awarded == expected_cap
    assert second_lang.rule_reference == "crs_core.second_official_language"
    assert second_lang.explanation.explanation_code == "core.language.second"
    assert second_lang.explanation.rule_path.startswith("crs_core.")
    _assert_explanations_present(result)


def test_additional_points_pnp_and_sibling():
    service = CRSEngineService()
    cfg = ConfigService().get_domain_rules()
    profile = CRSProfileInput(
        age=32,
        marital_status=MaritalStatus.SINGLE,
        education_level=EducationLevel.MASTERS_OR_PROFESSIONAL,
        first_official_language=LanguageCLBProfile(reading=9, writing=9, listening=9, speaking=9),
        canadian_work_experience_years=2,
        foreign_work_experience_years=1,
        has_provincial_nomination=True,
        has_sibling_in_canada=True,
    )

    result = service.compute_for_profile(profile)
    points = {c.factor_code: c.points_awarded for c in result.factor_contributions}

    assert points["additional_provincial_nomination"] == cfg.crs_additional.provincial_nomination
    assert points["additional_sibling_in_canada"] == cfg.crs_additional.sibling_in_canada
    explanation = next(c.explanation for c in result.factor_contributions if c.factor_code == "additional_provincial_nomination")
    assert explanation.rule_path.startswith("crs_additional.")
    _assert_explanations_present(result)
    assert all(c.nl_explanation for c in result.factor_contributions)


def test_transferability_certificate_language_points():
    service = CRSEngineService()
    cfg = ConfigService().get_domain_rules()
    profile = CRSProfileInput(
        age=34,
        marital_status=MaritalStatus.SINGLE,
        education_level=EducationLevel.TWO_OR_MORE_CREDENTIALS,
        first_official_language=LanguageCLBProfile(reading=7, writing=7, listening=7, speaking=7),
        canadian_work_experience_years=1,
        foreign_work_experience_years=0,
        has_certificate_of_qualification=True,
    )

    result = service.compute_for_profile(profile)
    cert_factor = next(
        c for c in result.factor_contributions if c.factor_code == "transferability_certificate_language"
    )
    expected_points = 0
    for entry in cfg.crs_transferability.certificate_language:
        if entry.factor_two == "clb7_plus":
            expected_points = entry.points
    assert cert_factor.points_awarded == expected_points
    assert cert_factor.rule_reference == "crs_transferability.certificate_language"
    assert cert_factor.explanation.rule_path == "crs_transferability.certificate_language"
    _assert_explanations_present(result)


def test_adapter_builds_crs_profile_from_candidate():
    today = date.today()
    candidate = CandidateProfile(
        marital_status="married",
        date_of_birth=today.replace(year=today.year - 28),
        education=[
            EducationRecord(level="secondary"),
            EducationRecord(level="bachelor_three_year_plus"),
        ],
        language_tests=[
            LanguageTestResult(
                test_type="IELTS",
                test_date=today,
                listening_clb=9,
                reading_clb=9,
                writing_clb=9,
                speaking_clb=9,
            )
        ],
        work_experience=[
            WorkExperienceRecord(
                teer_level=1,
                is_canadian=True,
                start_date=today.replace(year=today.year - 2),
                end_date=today,
                is_continuous=True,
            ),
            WorkExperienceRecord(
                teer_level=2,
                is_canadian=False,
                start_date=today.replace(year=today.year - 4),
                end_date=today.replace(year=today.year - 3),
                is_continuous=True,
            ),
        ],
    )

    crs_profile = build_crs_profile_from_candidate(candidate)

    assert crs_profile.marital_status == MaritalStatus.MARRIED
    assert crs_profile.education_level == EducationLevel.BACHELOR_THREE_YEAR_PLUS
    assert crs_profile.canadian_work_experience_years >= 1
    assert crs_profile.foreign_work_experience_years >= 1


def test_nl_explanations_present():
    service = CRSEngineService()
    profile = CRSProfileInput(
        age=28,
        marital_status=MaritalStatus.SINGLE,
        education_level=EducationLevel.BACHELOR_THREE_YEAR_PLUS,
        first_official_language=LanguageCLBProfile(reading=8, writing=8, listening=9, speaking=8),
        canadian_work_experience_years=1,
        foreign_work_experience_years=0,
    )
    result = service.compute_for_profile(profile)
    assert all(c.nl_explanation is not None for c in result.factor_contributions)
    some = result.factor_contributions[0].nl_explanation
    assert some.title
    assert some.description

