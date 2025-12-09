from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from src.app.cases.repository import (
    CaseEventRepository,
    CaseRepository,
    CaseSnapshotRepository,
)
from src.app.config.case_types_service import CaseTypeConfigError, CaseTypesConfigService
from src.app.config.plans_service import (
    PlanCaseTypeNotAllowed,
    PlanFeatureDisabled,
    PlanQuotaExceeded,
    PlansConfigService,
)
from src.app.models.tenant import Tenant


@dataclass
class CaseHistoryResult:
    case_id: str
    version: int
    created_at: datetime
    source: str


class CaseHistoryService:
    """Coordinates persistence of case evaluations and audit events."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.case_repo = CaseRepository(db)
        self.snapshot_repo = CaseSnapshotRepository(db)
        self.event_repo = CaseEventRepository(db)
        self.plans = PlansConfigService()
        self.case_types = CaseTypesConfigService()

    def _get_tenant_and_plan(self, tenant_id: str):
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError("Tenant not found")
        try:
            plan = self.plans.get_plan(tenant.plan_code)
        except Exception as exc:  # PlanConfigError
            raise ValueError(str(exc)) from exc
        return tenant, plan

    def persist_evaluation(
        self,
        *,
        profile: dict[str, Any],
        program_eligibility: dict[str, Any],
        crs_breakdown: Optional[dict[str, Any]],
        required_artifacts: Optional[dict[str, Any]],
        config_fingerprint: Optional[dict[str, Any]],
        source: str,
        status: str = "evaluated",
        actor: str = "system",
        tenant_id: str,
        created_by_user_id: Optional[str],
        case_type: str,
    ) -> CaseHistoryResult:
        # Validate plan + case type + quotas
        _, plan = self._get_tenant_and_plan(tenant_id)
        self.case_types.require_case_type(case_type)
        self.plans.assert_feature(plan, "enable_case_history")
        active_cases = self.case_repo.count_active_cases(tenant_id)
        self.plans.assert_case_type_allowed(plan, case_type)
        self.plans.assert_active_case_quota(plan, active_cases)

        # Single transaction to ensure record + snapshot + event stay consistent.
        record = self.case_repo.create_case(
            profile=profile,
            program_eligibility=program_eligibility,
            crs_breakdown=crs_breakdown,
            required_artifacts=required_artifacts,
            config_fingerprint=config_fingerprint,
            source=source,
            status=status,
            tenant_id=tenant_id,
            created_by=actor,
            created_by_user_id=created_by_user_id,
            case_type=case_type,
        )

        snapshot_version = self.snapshot_repo.next_version(record.id)
        snapshot = self.snapshot_repo.create_snapshot(
            case_id=record.id,
            version=snapshot_version,
            profile=profile,
            program_eligibility=program_eligibility,
            crs_breakdown=crs_breakdown,
            required_artifacts=required_artifacts,
            config_fingerprint=config_fingerprint,
            source=source,
            tenant_id=tenant_id,
            case_type=case_type,
        )

        self.event_repo.log_event(
            event_type="EVALUATION_CREATED",
            case_id=record.id,
            actor=actor,
            tenant_id=tenant_id,
            metadata={"source": source, "version": snapshot_version},
        )

        self.db.commit()
        self.db.refresh(record)
        self.db.refresh(snapshot)

        return CaseHistoryResult(
            case_id=record.id,
            version=snapshot.version,
            created_at=record.created_at,
            source=record.source,
        )

