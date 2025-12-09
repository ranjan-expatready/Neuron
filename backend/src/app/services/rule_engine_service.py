from __future__ import annotations

from src.app.rules.config_loader import load_domain_rules_config
from src.app.rules.config_port import RuleConfigPort
from src.app.rules.engine import RuleEngine
from src.app.rules.models import CandidateProfile, ProgramEvaluationResult


class RuleEngineService:
    """
    Facade for rule engine evaluation.
    Not wired to API yet; intended for downstream services/controllers.
    """

    def __init__(self, config_port: RuleConfigPort | None = None) -> None:
        if config_port:
            config = config_port.get_config()
        else:
            config = load_domain_rules_config()
        self.engine = RuleEngine(config=config)

    def evaluate(self, profile: CandidateProfile) -> dict[str, ProgramEvaluationResult]:
        return self.engine.evaluate_candidate(profile)
