import pytest

from src.app.config.case_types_service import CaseTypeConfigError, CaseTypesConfigService
from src.app.config.plans_service import (
    PlanCaseTypeNotAllowed,
    PlanFeatureDisabled,
    PlanQuotaExceeded,
    PlansConfigService,
)


def test_plans_load_and_defaults():
    service = PlansConfigService()
    config = service.load()
    codes = {plan.plan_code for plan in config.plans}
    assert "starter" in codes
    plan = service.get_plan("starter")
    assert plan.features.enable_case_history is True
    assert plan.features.enable_case_lifecycle is False


def test_case_types_load():
    service = CaseTypesConfigService()
    config = service.load()
    codes = {ct.code for ct in config.case_types}
    assert "express_entry_basic" in codes


def test_plan_gating_errors():
    plans = PlansConfigService()
    starter = plans.get_plan("starter")

    with pytest.raises(PlanCaseTypeNotAllowed):
        plans.assert_case_type_allowed(starter, "family_class")

    with pytest.raises(PlanQuotaExceeded):
        plans.assert_active_case_quota(starter, starter.quotas.max_active_cases)

    with pytest.raises(PlanFeatureDisabled):
        plans.assert_feature(starter, "enable_case_lifecycle")


def test_case_type_validation_error():
    service = CaseTypesConfigService()
    with pytest.raises(CaseTypeConfigError):
        service.require_case_type("nonexistent_case_type")

