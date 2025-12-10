from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.app.api.dependencies import get_current_user
from src.app.config.intake_config import (
    DocumentDefinition,
    FieldDefinition,
    FormDefinition,
    IntakeStep,
    IntakeTemplate,
    load_intake_bundle,
)
from src.app.config.options_config import load_options_config
from src.app.models.user import User
from src.app.security.errors import ForbiddenError, TenantAccessError

router = APIRouter()


def _require_admin_or_rcic(user: User):
    if not user.tenant_id:
        raise TenantAccessError("Tenant context required")
    if user.role not in ("admin", "owner", "rcic", "rcic_admin"):
        raise ForbiddenError("Admin intake config requires admin/RCIC role")


class ResolvedStep(IntakeStep):
    fields: List[FieldDefinition]


class ResolvedTemplate(IntakeTemplate):
    steps: List[ResolvedStep]


@router.get("/fields", response_model=List[FieldDefinition])
async def list_fields(current_user: User = Depends(get_current_user)):
    _require_admin_or_rcic(current_user)
    bundle = load_intake_bundle()
    return bundle.fields


@router.get("/templates", response_model=List[IntakeTemplate])
async def list_templates(
    resolved: bool = Query(False, description="If true, include resolved field definitions"),
    current_user: User = Depends(get_current_user),
):
    _require_admin_or_rcic(current_user)
    bundle = load_intake_bundle()
    if not resolved:
        return bundle.templates

    field_map = {f.id: f for f in bundle.fields}
    resolved_templates: List[ResolvedTemplate] = []
    for tpl in bundle.templates:
        steps: List[ResolvedStep] = []
        for step in tpl.steps:
            resolved_fields = [field_map[fid] for fid in step.fields if fid in field_map]
            steps.append(ResolvedStep(id=step.id, label=step.label, fields=resolved_fields))
        resolved_templates.append(
            ResolvedTemplate(
                id=tpl.id,
                label=tpl.label,
                applicable_programs=tpl.applicable_programs,
                applicable_plans=tpl.applicable_plans,
                steps=steps,
            )
        )
    return resolved_templates


@router.get("/documents", response_model=List[DocumentDefinition])
async def list_documents(current_user: User = Depends(get_current_user)):
    _require_admin_or_rcic(current_user)
    bundle = load_intake_bundle()
    return bundle.documents


@router.get("/forms", response_model=List[FormDefinition])
async def list_forms(current_user: User = Depends(get_current_user)):
    _require_admin_or_rcic(current_user)
    bundle = load_intake_bundle()
    return bundle.forms


@router.get("/options")
async def list_options(
    name: Optional[str] = Query(None, description="Filter by option set name"),
    current_user: User = Depends(get_current_user),
):
    _require_admin_or_rcic(current_user)
    bundle = load_options_config()
    if name:
        if name not in bundle.options:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Options not found")
        return {name: [opt.dict() for opt in bundle.options[name]]}
    return {k: [opt.dict() for opt in v] for k, v in bundle.options.items()}

