"""
Deprecated stub port kept for backward compatibility. The live engine now
loads config via DomainRulesConfig from YAML (see config_loader.py).
"""

from typing import Protocol

from .config_models import DomainRulesConfig


class RuleConfigPort(Protocol):
    def get_config(self) -> DomainRulesConfig:
        ...
