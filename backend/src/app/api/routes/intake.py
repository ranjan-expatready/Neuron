from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_current_user
from src.app.cases.repository import CaseRepository
from src.app.db.database import get_db
from src.app.models.user import User
from src.app.security.errors import TenantAccessError
from src.app.services.intake_engine import IntakeEngine


router = APIRouter()


class IntakeFieldResponse(BaseModel):
    id: str
    label: str
    data_path: str
    type: str
    ui_control: Optional[str] = None
    options_ref: Optional[object] = None
    validations: dict = Field(default_factory=dict)
    visibility_conditions: Optional[object] = None
    group: Optional[str] = None
    help_text: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    required: Optional[bool] = None


class IntakeStepResponse(BaseModel):
    id: str
    label: str
    fields: list[IntakeFieldResponse]


class IntakeSchemaResponse(BaseModel):
    program_code: str
    plan_code: Optional[str] = None
    template_id: str
    label: str
    steps: list[IntakeStepResponse]


class DocumentRequirementResponse(BaseModel):
    id: str
    label: str
    category: str
    required: bool
    reasons: list[str] = Field(default_factory=list)


@router.get("/intake-schema", response_model=IntakeSchemaResponse)
async def get_intake_schema(
    program_code: str = Query(..., alias="program_code"),
    plan_code: Optional[str] = Query(None, alias="plan_code"),
    current_user: User = Depends(get_current_user),
):
    _ = current_user  # enforced via dependency
    engine = IntakeEngine()
    try:
        schema = engine.get_intake_schema_for_program(program_code, plan_code)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err)) from err

    return IntakeSchemaResponse(
        program_code=program_code,
        plan_code=plan_code,
        template_id=schema.id,
        label=schema.label,
        steps=[
            IntakeStepResponse(
                id=step.id,
                label=step.label,
                fields=[IntakeFieldResponse(**asdict(fld)) for fld in step.fields],
            )
            for step in schema.steps
        ],
    )


@router.get("/document-checklist/{case_id}", response_model=list[DocumentRequirementResponse])
async def get_document_checklist(
    case_id: str,
    program_code: Optional[str] = Query(None, alias="program_code"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.tenant_id:
        raise TenantAccessError("Tenant context required")
    repo = CaseRepository(db)
    case = repo.get_case(case_id, tenant_id=current_user.tenant_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    engine = IntakeEngine()
    try:
        checklist = engine.get_document_checklist_for_case(case, program_code)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err

    return [DocumentRequirementResponse(**asdict(item)) for item in checklist]


__all__ = ["router"]

