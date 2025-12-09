from datetime import date

from src.app.domain.crs.models import (
    CRSProfileInput,
    EducationLevel,
    LanguageCLBProfile,
    MaritalStatus,
)
from src.app.services.crs_engine import CRSEngineService


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

