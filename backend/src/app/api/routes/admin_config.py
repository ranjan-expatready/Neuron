from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from src.app.admin_config.service import AdminConfigService, DomainConfigSnapshot
from src.app.api.dependencies import get_current_user
from src.app.domain_config.service import ConfigService
from src.app.documents.service import DocumentMatrixService
from src.app.models.user import User
from src.app.security.errors import ForbiddenError, TenantAccessError

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


def _require_admin_access(user: User):
    if not user.tenant_id:
        raise TenantAccessError("Tenant context required")
    if user.role not in ("admin", "owner"):
        raise ForbiddenError("Admin config requires admin/owner role")


@router.get("/", response_model=DomainConfigSnapshot)
async def get_full_domain_config(
    admin_config: AdminConfigService = Depends(get_admin_config_service),
    current_user: User = Depends(get_current_user),
):
    _require_admin_access(current_user)
    """Return the full domain configuration snapshot (read-only)."""
    return admin_config.get_full_snapshot()


@router.get("/sections", response_model=List[str])
async def get_config_sections(
    admin_config: AdminConfigService = Depends(get_admin_config_service),
    current_user: User = Depends(get_current_user),
):
    _require_admin_access(current_user)
    """List available configuration sections."""
    return admin_config.list_sections()


@router.get("/{section_name}", response_model=Dict[str, Any])
async def get_config_section(
    section_name: str,
    admin_config: AdminConfigService = Depends(get_admin_config_service),
    current_user: User = Depends(get_current_user),
):
    """Return a specific configuration section by name."""
    _require_admin_access(current_user)
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


