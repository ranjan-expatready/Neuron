from pathlib import Path

import yaml

from src.app.rules.config_loader import DomainRulesConfigService


def write_yaml(tmp_path: Path, name: str, data: dict) -> None:
    (tmp_path / f"{name}.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")


def minimal_configs(tmp_path: Path) -> None:
    write_yaml(
        tmp_path,
        "crs",
        {
            "crs_core": {"base_age_points": 50, "language_bonus_per_clb": 2},
            "crs_transferability": {"notes": "placeholder"},
        },
    )
    write_yaml(
        tmp_path,
        "language",
        {
            "program_minima": {
                "fsw_min_clb": 7,
                "cec_min_clb_teer_0_1": 7,
                "cec_min_clb_teer_2_3": 5,
            }
        },
    )
    write_yaml(
        tmp_path,
        "work_experience",
        {
            "eligible_teers": [0, 1, 2, 3],
            "fsw": {"min_continuous_months": 12},
            "cec": {"min_canadian_months": 12, "recency_years": 3},
        },
    )
    write_yaml(
        tmp_path,
        "proof_of_funds",
        {"table": [{"family_size": 1, "amount_cad": 13000.0}], "exemptions": ["CEC"]},
    )
    write_yaml(
        tmp_path,
        "programs",
        {
            "program_rules": [
                {"code": "FSW", "uses_proof_of_funds": True},
                {"code": "CEC", "uses_proof_of_funds": False},
            ]
        },
    )
    write_yaml(
        tmp_path,
        "arranged_employment",
        {
            "arranged_employment": {
                "valid_teers": [0, 1, 2, 3],
                "min_duration_months": 12,
                "require_full_time": True,
                "require_non_seasonal": True,
            }
        },
    )
    write_yaml(
        tmp_path,
        "biometrics_medicals",
        {
            "biometrics_medicals": {
                "medical_validity_months": 12,
                "biometrics_validity_months": 120,
                "expiry_warning_days": 90,
            }
        },
    )


def test_loads_minimal_config(tmp_path):
    minimal_configs(tmp_path)
    svc = DomainRulesConfigService(base_path=tmp_path)
    cfg = svc.load()
    assert cfg.language.fsw_min_clb == 7
    assert cfg.work_experience.fsw.min_continuous_months == 12
    assert cfg.proof_of_funds.table[0].amount_cad == 13000.0
    assert cfg.program_rules.get("CEC").uses_proof_of_funds is False


def test_missing_file_raises(tmp_path):
    minimal_configs(tmp_path)
    (tmp_path / "language.yaml").unlink()
    svc = DomainRulesConfigService(base_path=tmp_path)
    try:
        svc.load()
    except FileNotFoundError:
        return
    raise AssertionError("Expected FileNotFoundError for missing language.yaml")


def test_invalid_config_raises(tmp_path):
    minimal_configs(tmp_path)
    # Introduce an invalid type
    write_yaml(tmp_path, "crs", {"crs_core": {"base_age_points": "oops"}})
    svc = DomainRulesConfigService(base_path=tmp_path)
    try:
        svc.load()
    except ValueError as exc:
        assert "Invalid domain rules config" in str(exc)
        return
    raise AssertionError("Expected ValueError for invalid config types")
