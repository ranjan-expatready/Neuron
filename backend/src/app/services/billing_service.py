from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from sqlalchemy.orm import Session

from src.app.models.billing import TenantBillingState
from src.app.observability.logging import get_logger, log_error, log_info
from src.app.observability.metrics import metrics_registry
from src.app.security.errors import PlanLimitError, TenantAccessError

DEFAULT_PLAN_CONFIG: Dict[str, Any] = {
    "default_plan": "starter",
    "plans": {
        "starter": {
            "label": "Starter",
            "limits": {
                "max_cases": 50,
                "max_evaluations_per_month": 200,
                "express_entry_enabled": True,
                "lifecycle_transitions_enabled": True,
                "document_generation_enabled": True,
            },
        }
    },
}


class BillingService:
    """Lightweight billing abstraction (plan enforcement + usage tracking)."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = get_logger(__name__)
        self.plan_config = self._load_plan_config()

    def _plans_path(self) -> Path:
        return Path(__file__).resolve().parents[4] / "config" / "plans.yaml"

    def _load_plan_config(self) -> Dict[str, Any]:
        """Load plan configuration from config/plans.yaml with safe fallback."""
        path = self._plans_path()
        if path.exists():
            try:
                return yaml.safe_load(path.read_text()) or DEFAULT_PLAN_CONFIG
            except Exception:
                return DEFAULT_PLAN_CONFIG
        return DEFAULT_PLAN_CONFIG

    def _get_plan(self, plan_code: str) -> Dict[str, Any]:
        plans = self.plan_config.get("plans", {})
        if plan_code not in plans:
            raise ValueError(f"Unknown plan code '{plan_code}'")
        return plans[plan_code]

    def _default_plan_code(self) -> str:
        return self.plan_config.get("default_plan", "starter")

    def _get_or_create_state(self, tenant_id: str) -> TenantBillingState:
        if not tenant_id:
            raise TenantAccessError("Tenant context required for billing")
        state = self.db.query(TenantBillingState).filter_by(tenant_id=tenant_id).first()
        if state:
            return state

        state = TenantBillingState(
            tenant_id=tenant_id,
            plan_code=self._default_plan_code(),
            subscription_status="active",
            usage_counters={},
        )
        self.db.add(state)
        self.db.commit()
        self.db.refresh(state)
        log_info(
            logger=self.logger,
            message="billing.plan_initialized",
            tenant_id=tenant_id,
            component="billing",
            extra_fields={"plan_code": state.plan_code},
        )
        metrics_registry.record_billing_event("plan_initialized")
        return state

    def get_plan_status(self, tenant_id: str) -> Dict[str, Any]:
        state = self._get_or_create_state(tenant_id)
        plan = self._get_plan(state.plan_code)
        return {
            "tenant_id": tenant_id,
            "plan_code": state.plan_code,
            "subscription_status": state.subscription_status,
            "renewal_date": state.renewal_date.isoformat() if state.renewal_date else None,
            "limits": plan.get("limits", {}),
            "usage_counters": state.usage_counters or {},
        }

    def set_plan_status(
        self,
        tenant_id: str,
        plan_code: str,
        subscription_status: Optional[str] = None,
        renewal_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        plan = self._get_plan(plan_code)
        state = self._get_or_create_state(tenant_id)
        state.plan_code = plan_code
        if subscription_status:
            state.subscription_status = subscription_status
        state.renewal_date = renewal_date
        self.db.commit()
        self.db.refresh(state)
        log_info(
            logger=self.logger,
            message="billing.plan_updated",
            tenant_id=tenant_id,
            component="billing",
            extra_fields={"plan_code": plan_code, "subscription_status": state.subscription_status},
        )
        metrics_registry.record_billing_event("plan_updated")
        return {
            "plan": plan,
            "state": {
                "plan_code": state.plan_code,
                "subscription_status": state.subscription_status,
                "renewal_date": state.renewal_date.isoformat() if state.renewal_date else None,
            },
        }

    def _period_key(self) -> str:
        now = datetime.utcnow()
        return f"{now.year:04d}-{now.month:02d}"

    def _current_total(self, state: TenantBillingState, event_name: str) -> int:
        counters = state.usage_counters or {}
        event_data: Dict[str, Any] = counters.get(event_name, {})
        return int(event_data.get("total", 0))

    def _current_monthly(self, state: TenantBillingState, event_name: str, period_key: str) -> int:
        counters = state.usage_counters or {}
        event_data: Dict[str, Any] = counters.get(event_name, {})
        monthly = event_data.get("monthly", {})
        return int(monthly.get(period_key, 0))

    def record_usage_event(self, tenant_id: str, event_name: str) -> Dict[str, Any]:
        state = self._get_or_create_state(tenant_id)
        counters: Dict[str, Any] = state.usage_counters or {}
        event_data: Dict[str, Any] = counters.get(event_name, {"total": 0, "monthly": {}})
        event_data["total"] = int(event_data.get("total", 0)) + 1
        period_key = self._period_key()
        monthly = event_data.get("monthly", {})
        monthly[period_key] = int(monthly.get(period_key, 0)) + 1
        event_data["monthly"] = monthly
        counters[event_name] = event_data
        state.usage_counters = counters
        self.db.commit()
        self.db.refresh(state)
        log_info(
            logger=self.logger,
            message="billing.usage_recorded",
            tenant_id=tenant_id,
            component="billing",
            extra_fields={"event": event_name, "total": event_data["total"], "period": period_key},
        )
        metrics_registry.record_billing_event(event_name)
        return state.usage_counters

    def get_usage_snapshot(self, tenant_id: str) -> Dict[str, Any]:
        state = self._get_or_create_state(tenant_id)
        return {
            "tenant_id": tenant_id,
            "plan_code": state.plan_code,
            "subscription_status": state.subscription_status,
            "usage_counters": state.usage_counters or {},
        }

    def _raise_limit_error(
        self,
        *,
        tenant_id: str,
        plan_code: str,
        limit_name: str,
        detail: str,
    ) -> None:
        metrics_registry.record_plan_limit_violation(plan_code, limit_name)
        log_error(
            logger=self.logger,
            message="billing.plan_limit_exceeded",
            tenant_id=tenant_id,
            component="billing",
            extra_fields={"plan_code": plan_code, "limit": limit_name, "detail": detail},
        )
        raise PlanLimitError(detail)

    def apply_plan_limits(self, tenant_id: str, event_name: str) -> None:
        state = self._get_or_create_state(tenant_id)
        plan = self._get_plan(state.plan_code)
        limits = plan.get("limits", {})
        period_key = self._period_key()

        if event_name == "case_created":
            max_cases = limits.get("max_cases")
            if max_cases is not None and self._current_total(state, event_name) >= int(max_cases):
                self._raise_limit_error(
                    tenant_id=tenant_id,
                    plan_code=state.plan_code,
                    limit_name="max_cases",
                    detail="You have exceeded the case limit for your plan.",
                )
        elif event_name == "evaluation_run":
            if not limits.get("express_entry_enabled", True):
                self._raise_limit_error(
                    tenant_id=tenant_id,
                    plan_code=state.plan_code,
                    limit_name="express_entry_enabled",
                    detail="Your plan does not include Express Entry evaluations.",
                )
            max_eval = limits.get("max_evaluations_per_month")
            if max_eval is not None and self._current_monthly(state, event_name, period_key) >= int(
                max_eval
            ):
                self._raise_limit_error(
                    tenant_id=tenant_id,
                    plan_code=state.plan_code,
                    limit_name="max_evaluations_per_month",
                    detail="You have exceeded the monthly evaluation limit for your plan.",
                )
        elif event_name == "lifecycle_transition":
            if not limits.get("lifecycle_transitions_enabled", True):
                self._raise_limit_error(
                    tenant_id=tenant_id,
                    plan_code=state.plan_code,
                    limit_name="lifecycle_transitions_enabled",
                    detail="Your plan does not allow lifecycle transitions.",
                )
        elif event_name == "document_generated":
            if not limits.get("document_generation_enabled", True):
                self._raise_limit_error(
                    tenant_id=tenant_id,
                    plan_code=state.plan_code,
                    limit_name="document_generation_enabled",
                    detail="Your plan does not allow document generation.",
                )
            max_docs = limits.get("max_documents_per_month")
            if max_docs is not None and self._current_monthly(state, event_name, period_key) >= int(
                max_docs
            ):
                self._raise_limit_error(
                    tenant_id=tenant_id,
                    plan_code=state.plan_code,
                    limit_name="max_documents_per_month",
                    detail="You have exceeded the monthly document generation limit for your plan.",
                )

