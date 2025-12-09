from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from src.app.rules.config_loader import DomainRulesConfigService
from src.app.rules.config_models import (
    ArrangedEmploymentConfig,
    BiometricsMedicalsConfig,
    ClbTablesConfig,
    CrsCoreConfig,
    CrsTransferabilityConfig,
    DomainRulesConfig,
    LanguageConfig,
    ProgramRulesConfig,
    ProofOfFundsConfig,
    WorkExperienceConfig,
)


class DomainConfigBundle(BaseModel):
    """Aggregated, typed view of all domain rule configs."""

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

    def to_domain_rules(self) -> DomainRulesConfig:
        """Convert back to the canonical DomainRulesConfig model."""
        return DomainRulesConfig(**self.dict())


class ConfigService:
    """
    Loads and caches domain configs from config/domain/*.yaml.
    Intended as the single backend entrypoint for domain configuration access.
    """

    def __init__(self, base_path: Optional[Path] = None) -> None:
        self.base_path = base_path
        self._bundle: Optional[DomainConfigBundle] = None

    def load_bundle(self) -> DomainConfigBundle:
        """Load all domain configs into a typed bundle (cached per instance)."""
        if self._bundle is None:
            loader = DomainRulesConfigService(base_path=self.base_path)
            domain_rules = loader.load()
            self._bundle = DomainConfigBundle(**domain_rules.dict())
        return self._bundle

    def get_domain_rules(self) -> DomainRulesConfig:
        """Return the canonical DomainRulesConfig."""
        return self.load_bundle().to_domain_rules()

    # Convenience getters for callers that want a specific slice.
    def get_crs_core(self) -> CrsCoreConfig:
        return self.load_bundle().crs_core

    def get_language(self) -> LanguageConfig:
        return self.load_bundle().language

    def get_work_experience(self) -> WorkExperienceConfig:
        return self.load_bundle().work_experience

    def get_proof_of_funds(self) -> ProofOfFundsConfig:
        return self.load_bundle().proof_of_funds

    def get_program_rules(self) -> ProgramRulesConfig:
        return self.load_bundle().program_rules

    def get_arranged_employment(self) -> ArrangedEmploymentConfig:
        return self.load_bundle().arranged_employment

    def get_biometrics_medicals(self) -> BiometricsMedicalsConfig:
        return self.load_bundle().biometrics_medicals

