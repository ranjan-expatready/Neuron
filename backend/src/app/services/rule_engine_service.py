from __future__ import annotations

from src.app.domain_config.service import ConfigService
from src.app.rules.config_port import RuleConfigPort
from src.app.rules.crs_adapter import build_crs_profile_from_candidate
from src.app.rules.crs_engine import CRSEngine
from src.app.rules.engine import RuleEngine
from src.app.rules.models import (
    CandidateProfile,
    ProgramEvaluationResult,
    ProgramEligibilitySummary,
)
from src.app.rules.program_eligibility import evaluate_programs


class RuleEngineService:
    """
    Facade for rule engine evaluation.
    Not wired to API yet; intended for downstream services/controllers.
    """

    def __init__(
        self, config_port: RuleConfigPort | None = None, config_service: ConfigService | None = None
    ) -> None:
        if config_port:
            config = config_port.get_config()
        else:
            service = config_service or ConfigService()
            config = service.get_domain_rules()
        self.engine = RuleEngine(config=config)
        self._domain_config = config

    def evaluate(self, profile: CandidateProfile) -> dict[str, ProgramEvaluationResult]:
        return self.engine.evaluate_candidate(profile)

    def evaluate_programs(self, profile: CandidateProfile) -> ProgramEligibilitySummary:
        return evaluate_programs(profile, self.engine.config)

    def evaluate_full_profile(self, profile: CandidateProfile) -> dict[str, object]:
        """
        Combined view: program eligibility + CRS breakdown (DRAFT).
        """
        program_summary = self.evaluate_programs(profile)
        crs_results = self.evaluate(profile)
        return {"programs": program_summary, "crs": crs_results}

    def compute_crs(self, profile: CandidateProfile):
        crs_profile = build_crs_profile_from_candidate(profile)
        crs_engine = CRSEngine(config=self._domain_config)
        result = crs_engine.compute(crs_profile)
        return result
