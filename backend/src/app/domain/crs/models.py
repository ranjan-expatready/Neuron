from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator


class MaritalStatus(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    COMMON_LAW = "common_law"

    @property
    def with_spouse(self) -> bool:
        return self in {MaritalStatus.MARRIED, MaritalStatus.COMMON_LAW}


class EducationLevel(str, Enum):
    LESS_THAN_SECONDARY = "less_than_secondary"
    SECONDARY = "secondary"
    ONE_YEAR_POST_SECONDARY = "one_year_post_secondary"
    TWO_YEAR_POST_SECONDARY = "two_year_post_secondary"
    BACHELOR_THREE_YEAR_PLUS = "bachelor_three_year_plus"
    TWO_OR_MORE_CREDENTIALS = "two_or_more_credentials"
    MASTERS_OR_PROFESSIONAL = "masters_or_professional"
    DOCTORATE = "doctorate"


class LanguageCLBProfile(BaseModel):
    reading: int
    writing: int
    listening: int
    speaking: int

    def min_clb(self) -> int:
        return min(self.reading, self.writing, self.listening, self.speaking)


class CRSProfileInput(BaseModel):
    age: int
    marital_status: MaritalStatus = MaritalStatus.SINGLE
    education_level: EducationLevel
    first_official_language: LanguageCLBProfile
    second_official_language: Optional[LanguageCLBProfile] = None
    canadian_work_experience_years: int = 0
    foreign_work_experience_years: int = 0
    spouse_education_level: Optional[EducationLevel] = None
    spouse_language: Optional[LanguageCLBProfile] = None
    spouse_canadian_work_experience_years: Optional[int] = None
    has_certificate_of_qualification: bool = False
    has_valid_job_offer: bool = False
    job_offer_teer_category: Optional[str] = None
    has_provincial_nomination: bool = False
    has_sibling_in_canada: bool = False
    canadian_study_years: Optional[int] = None
    # For French bonus rules, we need to know whether French scores are present.
    first_language_is_french: bool = False

    @validator("age")
    def _age_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("age must be non-negative")
        return value

    @validator("canadian_work_experience_years", "foreign_work_experience_years")
    def _work_years_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("work experience years must be non-negative")
        return value


class CRSFactorContribution(BaseModel):
    factor_code: str
    points_awarded: int
    points_max: int
    inputs_used: Dict[str, Any] = Field(default_factory=dict)
    rule_reference: str
    explanation: Optional["CRSFactorExplanation"] = None
    nl_explanation: Optional["CRSFactorNLExplanation"] = None


class CRSFactorExplanation(BaseModel):
    explanation_code: str
    rule_path: str
    input_summary: Dict[str, Any] = Field(default_factory=dict)
    threshold_summary: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[Dict[str, Any]] = None


class CRSFactorNLExplanation(BaseModel):
    explanation_code: str
    title: str
    description: str
    improvement_hint: Optional[str] = None


class CRSResult(BaseModel):
    total_score: int
    factor_contributions: list[CRSFactorContribution] = Field(default_factory=list)


CRSFactorContribution.update_forward_refs()
