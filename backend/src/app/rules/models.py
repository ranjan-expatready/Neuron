from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, validator


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class RuleFlag(BaseModel):
    rule_id: str
    severity: Severity = Severity.INFO
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class LanguageTestResult(BaseModel):
    test_type: str
    test_date: Optional[date] = None
    expiry_date: Optional[date] = None
    listening_clb: Optional[int] = None
    reading_clb: Optional[int] = None
    writing_clb: Optional[int] = None
    speaking_clb: Optional[int] = None

    def min_clb(self) -> Optional[int]:
        scores = [
            self.listening_clb,
            self.reading_clb,
            self.writing_clb,
            self.speaking_clb,
        ]
        filtered = [s for s in scores if s is not None]
        return min(filtered) if filtered else None


class EducationRecord(BaseModel):
    level: str
    country: Optional[str] = None
    eca_received: bool = False
    eca_date: Optional[date] = None
    eca_expiry: Optional[date] = None


class WorkExperienceRecord(BaseModel):
    country: Optional[str] = None
    noc_code: Optional[str] = None
    teer_level: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    hours_per_week: Optional[float] = None
    is_continuous: bool = False
    is_canadian: bool = False
    is_paid: bool = True

    @validator("end_date")
    def _validate_dates(cls, v, values):
        start = values.get("start_date")
        if v and start and v < start:
            raise ValueError("end_date cannot precede start_date")
        return v


class ProofOfFundsSnapshot(BaseModel):
    amount: float
    currency: str = "CAD"
    as_of_date: date
    exemption_reason: Optional[str] = None


class JobOffer(BaseModel):
    employer_name: Optional[str] = None
    noc_code: Optional[str] = None
    teer_level: Optional[int] = None
    has_lmia: bool = False
    lmia_exemption_code: Optional[str] = None
    full_time: bool = True
    non_seasonal: bool = True
    duration_months: Optional[int] = None
    location_country: Optional[str] = None
    location_region: Optional[str] = None


class MedicalStatus(BaseModel):
    status: Optional[str] = None
    exam_date: Optional[date] = None
    expiry_date: Optional[date] = None


class BiometricsStatus(BaseModel):
    status: Optional[str] = None
    collection_date: Optional[date] = None
    expiry_date: Optional[date] = None


class CRSBreakdown(BaseModel):
    core_points: int = 0
    spouse_points: int = 0
    transferability_points: int = 0
    additional_points: int = 0

    @property
    def total_points(self) -> int:
        return (
            self.core_points
            + self.spouse_points
            + self.transferability_points
            + self.additional_points
        )


class ProgramEvaluationResult(BaseModel):
    program_code: str
    eligible: bool
    reasons: list[str] = Field(default_factory=list)
    flags: list[RuleFlag] = Field(default_factory=list)
    crs: Optional[CRSBreakdown] = None


class CandidateProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    marital_status: Optional[str] = None
    family_size: Optional[int] = 1
    education: list[EducationRecord] = Field(default_factory=list)
    work_experience: list[WorkExperienceRecord] = Field(default_factory=list)
    language_tests: list[LanguageTestResult] = Field(default_factory=list)
    proof_of_funds: list[ProofOfFundsSnapshot] = Field(default_factory=list)
    job_offers: list[JobOffer] = Field(default_factory=list)
    medical_status: Optional[MedicalStatus] = None
    biometrics_status: Optional[BiometricsStatus] = None
    nomination_points: int = 0  # placeholder for PNP add-ons

    def current_age(self, on_date: Optional[date] = None) -> Optional[int]:
        if not self.date_of_birth:
            return None
        ref = on_date or date.today()
        years = ref.year - self.date_of_birth.year
        if (ref.month, ref.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1
        return years

    def best_language_test(self) -> Optional[LanguageTestResult]:
        # Choose the test with the highest minimum CLB across skills.
        best: Optional[LanguageTestResult] = None
        best_min = -1
        for test in self.language_tests:
            min_clb = test.min_clb()
            if min_clb is None:
                continue
            if min_clb > best_min:
                best = test
                best_min = min_clb
        return best
