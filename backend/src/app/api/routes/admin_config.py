from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.app.admin_config.service import AdminConfigService, DomainConfigSnapshot
from src.app.config.case_types_service import CaseTypesConfigService
from src.app.config.plans_service import PlanFeatureDisabled, PlansConfigService
from src.app.db.database import get_db
from src.app.domain_config.service import ConfigService
from src.app.documents.service import DocumentMatrixService
from src.app.models.tenant import Tenant

router = APIRouter()


def get_config_service() -> ConfigService:
    return ConfigService()


def get_document_service(
    config_service: ConfigService = Depends(get_config_service),
) -> DocumentMatrixService:
    return DocumentMatrixService(config_service)


def get_admin_config_service(
    config_service: ConfigService = Depends(get_config_service),
    document_service: DocumentMatrixService = Depends(get_document_service),
) -> AdminConfigService:
    return AdminConfigService(config_service=config_service, document_service=document_service)


def _require_admin_feature(tenant_id: str, db: Session, plans: PlansConfigService) -> None:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found for admin access"
        )
    plan = plans.get_plan(tenant.plan_code)
    try:
        plans.assert_feature(plan, "enable_admin_config")
    except PlanFeatureDisabled as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get("/", response_model=DomainConfigSnapshot)
async def get_full_domain_config(
    tenant_id: str,
    admin_config: AdminConfigService = Depends(get_admin_config_service),
    db: Session = Depends(get_db),
):
    plans = PlansConfigService()
    _require_admin_feature(tenant_id, db, plans)
    """Return the full domain configuration snapshot (read-only)."""
    return admin_config.get_full_snapshot()


@router.get("/sections", response_model=List[str])
async def get_config_sections(
    tenant_id: str,
    admin_config: AdminConfigService = Depends(get_admin_config_service),
    db: Session = Depends(get_db),
):
    plans = PlansConfigService()
    _require_admin_feature(tenant_id, db, plans)
    """List available configuration sections."""
    return admin_config.list_sections()


@router.get("/plans", response_model=List[dict])
async def get_plans(tenant_id: str, db: Session = Depends(get_db)):
    plans_service = PlansConfigService()
    _require_admin_feature(tenant_id, db, plans_service)
    plans_config = plans_service.load()
    return [plan.dict() for plan in plans_config.plans]


@router.get("/case-types", response_model=List[dict])
async def get_case_types(tenant_id: str, db: Session = Depends(get_db)):
    plans_service = PlansConfigService()
    _require_admin_feature(tenant_id, db, plans_service)
    case_types = CaseTypesConfigService().load()
    return [ct.dict() for ct in case_types.case_types]


@router.get("/{section_name}", response_model=Dict[str, Any])
async def get_config_section(
    section_name: str,
    tenant_id: str,
    admin_config: AdminConfigService = Depends(get_admin_config_service),
    db: Session = Depends(get_db),
):
    """Return a specific configuration section by name."""
    plans = PlansConfigService()
    _require_admin_feature(tenant_id, db, plans)
    try:
        section = admin_config.get_section(section_name)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config section '{section_name}' not found",
        ) from exc

    # Pydantic models serialize cleanly; other objects are returned as-is.
    if hasattr(section, "dict"):
        return section.dict()
    return section


