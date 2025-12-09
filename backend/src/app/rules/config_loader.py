from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .config_models import (
    ArrangedEmploymentConfig,
    BiometricsMedicalsConfig,
    ClbTablesConfig,
    CrsCoreConfig,
    CrsTransferabilityConfig,
    DomainRulesConfig,
    LanguageConfig,
    ProgramRulesConfig,
    ProofOfFundsConfig,
    ProofOfFundsEntry,
    WorkExperienceConfig,
    WorkExperienceProgramRule,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
CONFIG_DIR = REPO_ROOT / "config" / "domain"


class DomainRulesConfigService:
    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = base_path or CONFIG_DIR
        self._config: DomainRulesConfig | None = None

    def load(self) -> DomainRulesConfig:
        if self._config is None:
            self._config = self._load_from_disk()
        return self._config

    def _load_yaml(self, name: str) -> dict[str, Any]:
        path = self.base_path / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Missing required config file: {path}")
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_from_disk(self) -> DomainRulesConfig:
        crs_data = self._load_yaml("crs")
        language_data = self._load_yaml("language")
        work_data = self._load_yaml("work_experience")
        pof_data = self._load_yaml("proof_of_funds")
        programs_data = self._load_yaml("programs")
        arranged_data = (
            self._load_yaml("arranged_employment")
            if (self.base_path / "arranged_employment.yaml").exists()
            else {}
        )
        biometrics_data = (
            self._load_yaml("biometrics_medicals")
            if (self.base_path / "biometrics_medicals.yaml").exists()
            else {}
        )

        try:
            proof_table = [ProofOfFundsEntry(**entry) for entry in pof_data.get("table", [])]
            work_cfg = WorkExperienceConfig(
                eligible_teers=work_data["eligible_teers"],
                fsw=WorkExperienceProgramRule(**work_data["fsw"]),
                cec=WorkExperienceProgramRule(**work_data["cec"]),
            )
            domain_cfg = DomainRulesConfig(
                crs_core=CrsCoreConfig(**crs_data["crs_core"]),
                crs_transferability=CrsTransferabilityConfig(
                    notes=crs_data.get("crs_transferability", {}).get("notes")
                ),
                language=LanguageConfig(
                    **language_data["program_minima"],
                    clb_tables_ref=language_data.get("clb_tables_ref"),
                ),
                clb_tables=ClbTablesConfig(
                    tables=language_data.get("clb_tables", []),
                ),
                work_experience=work_cfg,
                proof_of_funds=ProofOfFundsConfig(
                    table=proof_table,
                    exemptions=pof_data.get("exemptions", []),
                ),
                program_rules=ProgramRulesConfig(programs=programs_data.get("program_rules", [])),
                arranged_employment=ArrangedEmploymentConfig(
                    **arranged_data.get("arranged_employment", arranged_data or {})
                ),
                biometrics_medicals=BiometricsMedicalsConfig(
                    **biometrics_data.get("biometrics_medicals", biometrics_data or {})
                ),
            )
        except (TypeError, KeyError, ValidationError) as exc:
            raise ValueError(f"Invalid domain rules config: {exc}") from exc

        return domain_cfg


def load_domain_rules_config(base_path: Path | None = None) -> DomainRulesConfig:
    return DomainRulesConfigService(base_path).load()

