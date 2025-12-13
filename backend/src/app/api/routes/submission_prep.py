from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_current_user, get_db
from src.app.domain.forms.models import SubmissionPrepResult
from src.app.models.user import User
from src.app.security.errors import ForbiddenError, TenantAccessError
from src.app.services.submission_prep_engine import SubmissionPrepEngine, SubmissionPrepEngineError

router = APIRouter()


def _require_admin_or_rcic(user: User):
    if not user.tenant_id:
        raise TenantAccessError("Tenant context required")
    if user.role not in ("admin", "owner", "rcic", "rcic_admin"):
        raise ForbiddenError("Submission preparation requires admin/RCIC access")


@router.get(
    "/cases/{case_id}/submission/prep",
    response_model=SubmissionPrepResult,
    status_code=status.HTTP_200_OK,
)
def get_submission_prep(
    case_id: uuid.UUID,
    program_code: Optional[str] = Query(None),
    bundle_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Read-only preparation of submission-ready package for a case.
    Assembles forms, attachments, and readiness assessment.
    No DB writes, no external calls, no file operations.
    """
    _require_admin_or_rcic(current_user)
    engine = SubmissionPrepEngine()
    try:
        prep_result = engine.prepare_submission(
            case_id=str(case_id),
            program_code=program_code,
            bundle_id=bundle_id,
            tenant_id=str(current_user.tenant_id),
            db_session=db,
        )
        return prep_result
    except SubmissionPrepEngineError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
