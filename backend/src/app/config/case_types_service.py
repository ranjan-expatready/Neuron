from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError


REPO_ROOT = Path(__file__).resolve().parents[4]
CASE_TYPES_PATH = REPO_ROOT / "config" / "case_types.yaml"


class CaseTypeDefinition(BaseModel):
    code: str
    label: str
    program_categories: List[str] = Field(default_factory=list)
    required_data_blocks: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)

    class Config:
        extra = "forbid"


class CaseTypesConfig(BaseModel):
    case_types: List[CaseTypeDefinition]

    class Config:
        extra = "forbid"

    def by_code(self) -> Dict[str, CaseTypeDefinition]:
        return {ct.code: ct for ct in self.case_types}


class CaseTypeConfigError(Exception):
    """Raised when case type configuration is missing or invalid."""


class CaseTypesConfigService:
    """Loads and validates case type definitions."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or CASE_TYPES_PATH
        self._config: Optional[CaseTypesConfig] = None

    def load(self) -> CaseTypesConfig:
        if self._config is None:
            if not self.path.exists():
                raise CaseTypeConfigError(f"Missing case types configuration: {self.path}")
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                self._config = CaseTypesConfig(**data)
            except (ValidationError, TypeError) as exc:
                raise CaseTypeConfigError(f"Invalid case types configuration: {exc}") from exc
        return self._config

    def require_case_type(self, code: str) -> CaseTypeDefinition:
        case_types = self.load().by_code()
        if code not in case_types:
            raise CaseTypeConfigError(f"Case type '{code}' not defined")
        return case_types[code]

