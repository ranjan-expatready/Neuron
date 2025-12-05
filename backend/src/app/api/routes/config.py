from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.organization import Organization
from ...models.user import User
from ...schemas.config import ConfigCaseType, ConfigField, ConfigForm
from ...services.config import ConfigService
from ..dependencies import get_current_user, get_current_user_org

router = APIRouter()


@router.get("/case-types", response_model=list[ConfigCaseType])
async def get_case_types(is_active: Optional[bool] = Query(None), db: Session = Depends(get_db)):
    """Get all case types"""
    case_types = ConfigService.get_case_types(db, is_active)
    return case_types


@router.get("/case-types/{case_type_code}", response_model=dict[str, Any])
async def get_case_type_config(case_type_code: str, db: Session = Depends(get_db)):
    """Get complete configuration for a case type"""
    config = ConfigService.get_case_type_config(db, case_type_code)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case type not found")
    return config


@router.get("/case-types/{case_type_code}/forms", response_model=list[ConfigForm])
async def get_case_type_forms(
    case_type_code: str, is_active: Optional[bool] = Query(None), db: Session = Depends(get_db)
):
    """Get forms for a case type"""
    forms = ConfigService.get_forms_by_case_type(db, case_type_code, is_active)
    return forms


@router.get("/case-types/{case_type_code}/fields", response_model=list[ConfigField])
async def get_case_type_fields(
    case_type_code: str,
    form_code: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    """Get fields for a case type"""
    fields = ConfigService.get_fields_by_case_type(db, case_type_code, form_code, is_active)
    return fields


@router.get("/case-types/{case_type_code}/checklist")
async def get_case_type_checklist(
    case_type_code: str, is_active: Optional[bool] = Query(None), db: Session = Depends(get_db)
):
    """Get checklist for a case type"""
    checklist = ConfigService.get_checklist_by_case_type(db, case_type_code, is_active)
    return [
        {
            "item_code": item.item_code,
            "item_name": item.item_name,
            "description": item.description,
            "category": item.category,
            "is_required": item.is_required,
            "sort_order": item.sort_order,
            "conditions": item.conditions,
        }
        for item in checklist
    ]


@router.get("/templates/{template_code}")
async def get_template(template_code: str, db: Session = Depends(get_db)):
    """Get a template by code"""
    template = ConfigService.get_template_by_code(db, template_code)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return {
        "template_code": template.template_code,
        "name": template.name,
        "description": template.description,
        "template_type": template.template_type,
        "subject": template.subject,
        "content": template.content,
        "variables": template.variables,
    }


@router.get("/templates")
async def get_templates_by_type(template_type: str = Query(...), db: Session = Depends(get_db)):
    """Get templates by type"""
    templates = ConfigService.get_templates_by_type(db, template_type)
    return [
        {
            "template_code": template.template_code,
            "name": template.name,
            "description": template.description,
            "template_type": template.template_type,
            "subject": template.subject,
            "content": template.content,
            "variables": template.variables,
        }
        for template in templates
    ]


@router.get("/feature-flags/{flag_key}")
async def check_feature_flag(
    flag_key: str,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    """Check if a feature flag is enabled"""
    is_enabled = ConfigService.is_feature_enabled(db, flag_key, current_org.id, current_user.id)
    return {"flag_key": flag_key, "is_enabled": is_enabled}
