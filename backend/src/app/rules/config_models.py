from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class CrsAgeBand(BaseModel):
    min_age: int
    max_age: int
    single: int
    with_spouse: int


class CrsEducationPoints(BaseModel):
    level: str
    single: int
    with_spouse: int


class CrsLanguagePoints(BaseModel):
    clb: int
    single_per_skill: int
    with_spouse_per_skill: int


class CrsSecondLanguageConfig(BaseModel):
    rows: list[CrsLanguagePoints] = Field(default_factory=list)
    max_points_single: int = 24
    max_points_with_spouse: int = 22


class CrsCanadianWorkPoints(BaseModel):
    years: int
    single: int
    with_spouse: int


class CrsCoreConfig(BaseModel):
    age_bands: list[CrsAgeBand] = Field(default_factory=list)
    education: list[CrsEducationPoints] = Field(default_factory=list)
    first_official_language: list[CrsLanguagePoints] = Field(default_factory=list)
    second_official_language: CrsSecondLanguageConfig = Field(
        default_factory=CrsSecondLanguageConfig
    )
    canadian_work_experience: list[CrsCanadianWorkPoints] = Field(default_factory=list)
    # Legacy placeholders retained for backwards compatibility
    base_age_points: int = 0
    language_bonus_per_clb: int = 0


class SpouseEducationPoints(BaseModel):
    level: str
    points: int


class SpouseLanguagePoints(BaseModel):
    clb: int
    points_per_skill: int


class SpouseCanadianWorkPoints(BaseModel):
    years: int
    points: int


class CrsSpouseConfig(BaseModel):
    education: list[SpouseEducationPoints] = Field(default_factory=list)
    language: list[SpouseLanguagePoints] = Field(default_factory=list)
    canadian_work_experience: list[SpouseCanadianWorkPoints] = Field(default_factory=list)


class TransferabilityEntry(BaseModel):
    factor_one: str
    factor_two: str
    points: int


class TransferabilityCaps(BaseModel):
    per_bundle: int = 50
    total: int = 100


class CrsTransferabilityConfig(BaseModel):
    education_language: list[TransferabilityEntry] = Field(default_factory=list)
    education_canadian_work: list[TransferabilityEntry] = Field(default_factory=list)
    foreign_language: list[TransferabilityEntry] = Field(default_factory=list)
    foreign_canadian_work: list[TransferabilityEntry] = Field(default_factory=list)
    certificate_language: list[TransferabilityEntry] = Field(default_factory=list)
    caps: TransferabilityCaps = Field(default_factory=TransferabilityCaps)
    notes: Optional[str] = None


class CanadianStudyPoints(BaseModel):
    one_to_two_years: int = 0
    three_or_more_years: int = 0


class FrenchBonusEntry(BaseModel):
    condition: str
    points: int


class JobOfferBonusEntry(BaseModel):
    teer_category: str
    points: int


class CrsAdditionalPointsConfig(BaseModel):
    provincial_nomination: int = 0
    sibling_in_canada: int = 0
    canadian_study: CanadianStudyPoints = Field(default_factory=CanadianStudyPoints)
    french: list[FrenchBonusEntry] = Field(default_factory=list)
    job_offer: list[JobOfferBonusEntry] = Field(default_factory=list)


class LanguageProgramMinima(BaseModel):
    min_clb_all_skills: Optional[int] = None  # FSW
    min_clb_teer_0_1: Optional[int] = None  # CEC higher TEER
    min_clb_teer_2_3: Optional[int] = None  # CEC lower TEER
    min_clb_speak_listen_fst: Optional[int] = None
    min_clb_read_write_fst: Optional[int] = None


class LanguageConfig(BaseModel):
    fsw_min_clb: Optional[int] = None
    cec_min_clb_teer_0_1: Optional[int] = None
    cec_min_clb_teer_2_3: Optional[int] = None
    fst_min_clb_speak_listen: Optional[int] = None
    fst_min_clb_read_write: Optional[int] = None
    clb_tables_ref: Optional[str] = None


class ClbTableEntry(BaseModel):
    clb: int
    min_score: float
    max_score: Optional[float] = None
    skill: str
    test: str


class ClbTablesConfig(BaseModel):
    tables: list[ClbTableEntry] = Field(default_factory=list)


class WorkExperienceProgramRule(BaseModel):
    min_continuous_months: Optional[int] = None
    min_canadian_months: Optional[int] = None
    recency_years: Optional[int] = None


class WorkExperienceConfig(BaseModel):
    eligible_teers: list[int] = Field(default_factory=list)
    fsw: WorkExperienceProgramRule
    cec: WorkExperienceProgramRule


class ProofOfFundsEntry(BaseModel):
    family_size: int
    amount_cad: float
    effective_date: Optional[date] = None


class ProofOfFundsConfig(BaseModel):
    table: list[ProofOfFundsEntry] = Field(default_factory=list)
    exemptions: list[str] = Field(default_factory=list)


class ProgramRule(BaseModel):
    code: str
    requires_job_offer: bool = False
    requires_certificate_or_offer: bool = False
    uses_proof_of_funds: bool = True
    min_education_level: Optional[str] = None  # DRAFT: string label comparison only
    min_continuous_months: Optional[int] = None
    min_canadian_months: Optional[int] = None
    eligible_teers: list[int] = Field(default_factory=list)
    notes: Optional[str] = None


class ProgramRulesConfig(BaseModel):
    programs: list[ProgramRule] = Field(default_factory=list)

    def get(self, code: str) -> ProgramRule:
        for p in self.programs:
            if p.code == code:
                return p
        raise KeyError(f"Program rule not found for {code}")


class ArrangedEmploymentConfig(BaseModel):
    valid_teers: list[int] = Field(default_factory=list)
    min_duration_months: Optional[int] = None
    require_full_time: bool = True
    require_non_seasonal: bool = True


class BiometricsMedicalsConfig(BaseModel):
    medical_validity_months: Optional[int] = None
    biometrics_validity_months: Optional[int] = None
    expiry_warning_days: int = 90


class DomainRulesConfig(BaseModel):
    crs_core: CrsCoreConfig
    crs_spouse: CrsSpouseConfig
    crs_transferability: CrsTransferabilityConfig
    crs_additional: CrsAdditionalPointsConfig
    language: LanguageConfig
    clb_tables: ClbTablesConfig
    work_experience: WorkExperienceConfig
    proof_of_funds: ProofOfFundsConfig
    program_rules: ProgramRulesConfig
    arranged_employment: ArrangedEmploymentConfig
    biometrics_medicals: BiometricsMedicalsConfig

    class Config:
        extra = "forbid"
