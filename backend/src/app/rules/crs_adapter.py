from __future__ import annotations

from datetime import date
from typing import Optional

from src.app.domain.crs.models import (
    CRSProfileInput,
    EducationLevel,
    LanguageCLBProfile,
    MaritalStatus,
)
from src.app.rules.models import CandidateProfile


def _years_from_months(months: int) -> int:
    return months // 12


def _sum_months(records) -> int:
    total = 0
    for record in records:
        if not record.start_date:
            continue
        end = record.end_date or date.today()
        months = (end.year - record.start_date.year) * 12 + (end.month - record.start_date.month)
        total += max(0, months)
    return total


def _normalize_marital_status(raw: Optional[str]) -> MaritalStatus:
    if not raw:
        return MaritalStatus.SINGLE
    normalized = raw.lower()
    if normalized in {"married", "marital_married"}:
        return MaritalStatus.MARRIED
    if normalized in {"common_law", "common-law"}:
        return MaritalStatus.COMMON_LAW
    return MaritalStatus.SINGLE


def _highest_education_level(profile: CandidateProfile) -> EducationLevel:
    order = [
        EducationLevel.LESS_THAN_SECONDARY,
        EducationLevel.SECONDARY,
        EducationLevel.ONE_YEAR_POST_SECONDARY,
        EducationLevel.TWO_YEAR_POST_SECONDARY,
        EducationLevel.BACHELOR_THREE_YEAR_PLUS,
        EducationLevel.TWO_OR_MORE_CREDENTIALS,
        EducationLevel.MASTERS_OR_PROFESSIONAL,
        EducationLevel.DOCTORATE,
    ]
    level_map = {lvl.value: lvl for lvl in order}
    best = EducationLevel.LESS_THAN_SECONDARY
    for record in profile.education:
        candidate = level_map.get(record.level)
        if candidate and order.index(candidate) > order.index(best):
            best = candidate
    return best


def _language_from_best_test(profile: CandidateProfile) -> LanguageCLBProfile:
    best = profile.best_language_test()
    if not best:
        return LanguageCLBProfile(reading=0, writing=0, listening=0, speaking=0)
    return LanguageCLBProfile(
        reading=best.reading_clb or 0,
        writing=best.writing_clb or 0,
        listening=best.listening_clb or 0,
        speaking=best.speaking_clb or 0,
    )


def build_crs_profile_from_candidate(profile: CandidateProfile) -> CRSProfileInput:
    marital_status = _normalize_marital_status(profile.marital_status)
    age = profile.current_age() or 0
    education_level = _highest_education_level(profile)

    canadian_months = _sum_months([w for w in profile.work_experience if w.is_canadian])
    foreign_months = _sum_months([w for w in profile.work_experience if not w.is_canadian])

    return CRSProfileInput(
        age=age,
        marital_status=marital_status,
        education_level=education_level,
        first_official_language=_language_from_best_test(profile),
        second_official_language=None,
        canadian_work_experience_years=_years_from_months(canadian_months),
        foreign_work_experience_years=_years_from_months(foreign_months),
    )


