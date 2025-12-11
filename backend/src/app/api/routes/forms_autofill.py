from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_current_user, get_db
from src.app.domain.forms.models import FormAutofillPreviewResult
from src.app.models.user import User
from src.app.security.errors import ForbiddenError, TenantAccessError
from src.app.services.form_autofill_engine import FormAutofillEngine, FormAutofillEngineError

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

