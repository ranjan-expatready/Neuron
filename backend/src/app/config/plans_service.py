from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError


REPO_ROOT = Path(__file__).resolve().parents[4]
PLANS_PATH = REPO_ROOT / "config" / "plans.yaml"
DEFAULT_PLAN_CODE = "starter"


class PlanFeatures(BaseModel):
    enable_case_history: bool = False
    enable_case_lifecycle: bool = False
    enable_admin_config: bool = False


class PlanQuotas(BaseModel):
    max_active_cases: int = Field(..., ge=0)
    max_users: int = Field(..., ge=0)
    max_storage_gb: int = Field(..., ge=0)


class PlanDefinition(BaseModel):
    plan_code: str
    name: str
    description: Optional[str] = None
    features: PlanFeatures
    quotas: PlanQuotas
    allowed_case_types: List[str] = Field(default_factory=list)

    class Config:
        extra = "forbid"


class PlansConfig(BaseModel):
    plans: List[PlanDefinition]

    class Config:
        extra = "forbid"

    def by_code(self) -> Dict[str, PlanDefinition]:
        return {plan.plan_code: plan for plan in self.plans}


class PlanConfigError(Exception):
    """Raised when plan configuration is missing or invalid."""


class PlanFeatureDisabled(PlanConfigError):
    """Raised when a feature is not enabled for the tenant plan."""


class PlanQuotaExceeded(PlanConfigError):
    """Raised when a quota has been exceeded for the tenant plan."""


class PlanCaseTypeNotAllowed(PlanConfigError):
    """Raised when a case type is not allowed for the tenant plan."""


class PlansConfigService:
    """Loads pricing/plan definitions and provides gating helpers."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or PLANS_PATH
        self._config: Optional[PlansConfig] = None

    def load(self) -> PlansConfig:
        if self._config is None:
            if not self.path.exists():
                raise PlanConfigError(f"Missing plans configuration: {self.path}")
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                self._config = PlansConfig(**data)
            except (ValidationError, TypeError) as exc:
                raise PlanConfigError(f"Invalid plans configuration: {exc}") from exc
        return self._config

    def get_plan(self, plan_code: Optional[str]) -> PlanDefinition:
        config = self.load().by_code()
        plan = config.get(plan_code or DEFAULT_PLAN_CODE) or config.get(DEFAULT_PLAN_CODE)
        if not plan:
            raise PlanConfigError(f"Plan '{plan_code}' not found and default plan missing")
        return plan

    def assert_feature(self, plan: PlanDefinition, feature: str) -> None:
        if not getattr(plan.features, feature, False):
            raise PlanFeatureDisabled(f"Feature '{feature}' is disabled for plan '{plan.plan_code}'")

    def assert_case_type_allowed(self, plan: PlanDefinition, case_type: str) -> None:
        if plan.allowed_case_types and case_type not in plan.allowed_case_types:
            raise PlanCaseTypeNotAllowed(
                f"Case type '{case_type}' not allowed for plan '{plan.plan_code}'"
            )

    def assert_active_case_quota(self, plan: PlanDefinition, active_cases: int) -> None:
        if active_cases >= plan.quotas.max_active_cases:
            raise PlanQuotaExceeded(
                f"Active case quota exceeded for plan '{plan.plan_code}' "
                f"(limit={plan.quotas.max_active_cases}, current={active_cases})"
            )

