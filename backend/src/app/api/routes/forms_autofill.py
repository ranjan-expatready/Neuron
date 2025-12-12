from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_current_user, get_db
from src.app.config.form_config import FormBundleDefinition, FormConfigError, load_form_bundles
from src.app.domain.forms.models import FormAutofillPreviewResult
from src.app.domain.submission.models import SubmissionReadinessReport
from src.app.models.user import User
from src.app.security.errors import ForbiddenError, TenantAccessError
from src.app.services.form_autofill_engine import FormAutofillEngine, FormAutofillEngineError
from src.app.services.submission_readiness_service import (
    SubmissionReadinessError,
    SubmissionReadinessService,
)

router = APIRouter()


def _require_admin_or_rcic(user: User):
    if not user.tenant_id:
        raise TenantAccessError("Tenant context required")
    if user.role not in ("admin", "owner", "rcic", "rcic_admin"):
        raise ForbiddenError("Forms autofill preview requires admin/RCIC access")


@router.get(
    "/cases/{case_id}/forms/autofill-preview",
    response_model=FormAutofillPreviewResult,
    status_code=status.HTTP_200_OK,
)
def get_forms_autofill_preview(
    case_id: uuid.UUID,
    program_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Read-only preview of form autofill values for a case.
    No DB writes, no PDF generation, no submission.
    """
    _require_admin_or_rcic(current_user)
    engine = FormAutofillEngine()
    try:
        preview = engine.build_autofill_preview(
            case_id=str(case_id),
            program_code=program_code,
            tenant_id=str(current_user.tenant_id),
            db_session=db,
        )
        return preview
    except FormAutofillEngineError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "/cases/{case_id}/submission/readiness",
    response_model=SubmissionReadinessReport,
    status_code=status.HTTP_200_OK,
)
def get_submission_readiness(
    case_id: uuid.UUID,
    bundle_id: str = Query(..., description="Form bundle identifier"),
    program_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deterministic, read-only readiness report for submission.
    Uses autofill preview, form schemas, and document checklist. No writes.
    """
    _require_admin_or_rcic(current_user)
    service = SubmissionReadinessService()
    try:
        return service.generate_report(
            case_id=str(case_id),
            bundle_id=bundle_id,
            program_code=program_code,
            tenant_id=str(current_user.tenant_id),
            db_session=db,
        )
    except SubmissionReadinessError as exc:
        detail = str(exc)
        if "Case not found" in detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from exc
        if "Invalid bundle_id" in detail:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc


@router.get(
    "/config/form-bundles",
    response_model=list[FormBundleDefinition],
    status_code=status.HTTP_200_OK,
)
def list_form_bundles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Minimal read-only list of form bundles for UI dropdowns."""
    _require_admin_or_rcic(current_user)
    try:
        return load_form_bundles()
    except FormConfigError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

