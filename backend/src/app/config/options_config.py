from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError


class OptionsConfigError(Exception):
    """Base exception for options config issues."""


class OptionItem(BaseModel):
    value: Any
    label: str


class OptionsBundle(BaseModel):
    options: Dict[str, List[OptionItem]] = Field(default_factory=dict)


def _default_base_path() -> Path:
    return Path(__file__).resolve().parents[4] / "config" / "domain"


def _load_yaml(base_path: Path) -> dict[str, Any]:
    path = base_path / "options.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=4)
def load_options_config(base_path: Optional[str] = None) -> OptionsBundle:
    base = Path(base_path) if base_path else _default_base_path()
    raw = _load_yaml(base)
    try:
        options = {
            name: [OptionItem(**opt) for opt in opt_list]
            for name, opt_list in raw.get("options", {}).items()
            if isinstance(opt_list, list)
        }
        return OptionsBundle(options=options)
    except ValidationError as err:
        raise OptionsConfigError(f"Invalid options.yaml: {err}") from err


def clear_options_cache() -> None:
    load_options_config.cache_clear()

