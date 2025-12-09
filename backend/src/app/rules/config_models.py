from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class CrsCoreConfig(BaseModel):
    base_age_points: int = 0  # Placeholder; SME validation required.
    language_bonus_per_clb: int = 0  # Placeholder; SME validation required.


class CrsTransferabilityConfig(BaseModel):
    # Placeholder container for future wiring of transferability tables.
    notes: Optional[str] = None


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
    crs_transferability: CrsTransferabilityConfig
    language: LanguageConfig
    clb_tables: ClbTablesConfig
    work_experience: WorkExperienceConfig
    proof_of_funds: ProofOfFundsConfig
    program_rules: ProgramRulesConfig
    arranged_employment: ArrangedEmploymentConfig
    biometrics_medicals: BiometricsMedicalsConfig

    class Config:
        extra = "forbid"
