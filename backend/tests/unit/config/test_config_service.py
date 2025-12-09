from pathlib import Path

import pytest

from src.app.domain_config.service import ConfigService, DomainConfigBundle
from src.app.rules.config_models import DomainRulesConfig


def test_load_bundle_success_uses_repo_configs() -> None:
    service = ConfigService()
    bundle = service.load_bundle()

    assert isinstance(bundle, DomainConfigBundle)
    # Spot-check a few representative fields exist (structure only).
    assert bundle.language is not None
    assert bundle.work_experience is not None
    assert isinstance(bundle.program_rules.programs, list)


def test_to_domain_rules_round_trip() -> None:
    service = ConfigService()
    bundle = service.load_bundle()
    domain_rules = bundle.to_domain_rules()

    assert isinstance(domain_rules, DomainRulesConfig)
    assert domain_rules.proof_of_funds.table is not None


def test_missing_configs_raise(tmp_path: Path) -> None:
    service = ConfigService(base_path=tmp_path)
    with pytest.raises(FileNotFoundError):
        service.load_bundle()

