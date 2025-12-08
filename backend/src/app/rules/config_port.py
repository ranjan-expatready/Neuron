from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Protocol


@dataclass
class LanguageRuleConfig:
    # For FSW/FST generic minima
    min_clb_all_skills: Optional[int] = None
    # For CEC split by TEER
    min_clb_teer_0_1: Optional[int] = None
    min_clb_teer_2_3: Optional[int] = None


@dataclass
class WorkRuleConfig:
    min_continuous_months: Optional[int] = None
    require_canadian_months: Optional[int] = None
    recency_years: Optional[int] = None  # e.g., last 3 years for CEC
    eligible_teers: Optional[list[int]] = None


@dataclass
class FundsRuleConfig:
    required_amount: Optional[float] = None
    currency: str = "CAD"
    exemptions: list[str] = field(default_factory=list)


@dataclass
class ProgramRuleConfig:
    program_code: str
    language: LanguageRuleConfig
    work: WorkRuleConfig
    funds: FundsRuleConfig
    requires_job_offer: bool = False


@dataclass
class CRSConfig:
    # Placeholder until ENG-RULE-002 wires full tables.
    base_age_points: int = 50  # DRAFT/DUMMY
    language_bonus_per_clb: int = 2  # DRAFT/DUMMY


class RuleConfigPort(Protocol):
    def get_program_rules(self, program_code: str) -> ProgramRuleConfig:
        ...

    def get_crs_config(self) -> CRSConfig:
        ...


class InMemoryRuleConfigPort:
    """
    DRAFT stub. Values are placeholders for engine skeleton only.
    Real values will come from config/domain YAML in ENG-RULE-002.
    """

    def __init__(self) -> None:
        self._program_rules: dict[str, ProgramRuleConfig] = {
            "FSW": ProgramRuleConfig(
                program_code="FSW",
                language=LanguageRuleConfig(min_clb_all_skills=7),
                work=WorkRuleConfig(
                    min_continuous_months=12,
                    eligible_teers=[0, 1, 2, 3],
                ),
                funds=FundsRuleConfig(required_amount=13000.0, currency="CAD"),
                requires_job_offer=False,
            ),
            "CEC": ProgramRuleConfig(
                program_code="CEC",
                language=LanguageRuleConfig(
                    min_clb_teer_0_1=7,
                    min_clb_teer_2_3=5,
                ),
                work=WorkRuleConfig(
                    require_canadian_months=12,
                    recency_years=3,
                    eligible_teers=[0, 1, 2, 3],
                ),
                funds=FundsRuleConfig(
                    required_amount=None,
                    exemptions=["CEC"],
                ),
                requires_job_offer=False,
            ),
        }
        self._crs_config = CRSConfig()

    def get_program_rules(self, program_code: str) -> ProgramRuleConfig:
        if program_code not in self._program_rules:
            raise KeyError(f"Program rules not found for {program_code}")
        return self._program_rules[program_code]

    def get_crs_config(self) -> CRSConfig:
        return self._crs_config
