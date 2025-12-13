from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_current_user, get_db
from src.app.models.user import User
from src.app.security.errors import ForbiddenError, TenantAccessError
from src.app.services.submission_readiness import (
    ENGINE_VERSION,
    SubmissionReadinessEngine,
    SubmissionReadinessEngineError,
    SubmissionReadinessResult,
)
from src.app.services.submission_readiness_verification import (
    EvidenceBundle,
    SubmissionReadinessVerificationService,
)
from src.app.services.submission_preparation import (
    SubmissionPreparationPackage,
    SubmissionPreparationService,
    SubmissionPreparationServiceError,
)
from src.app.services.assisted_drafts import AssistedDraftBundle, AssistedDraftService, AssistedDraftsError

router = APIRouter()


def _require_admin_or_rcic(user: User):
    if not user.tenant_id:
        raise TenantAccessError("Tenant context required")
    if user.role not in ("admin", "owner", "rcic", "rcic_admin"):
        raise ForbiddenError("Submission readiness requires admin/RCIC access")


@router.get(
    "/cases/{case_id}/submission-readiness",
    response_model=SubmissionReadinessResult,
    status_code=status.HTTP_200_OK,
)
def get_submission_readiness(
    case_id: uuid.UUID,
    program_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Read-only submission readiness evaluation.
    Uses config-driven document requirements and existing case documents.
    """
    _require_admin_or_rcic(current_user)
    engine = SubmissionReadinessEngine()
    try:
        return engine.evaluate_case(
            case_id=str(case_id),
            program_code=program_code,
            tenant_id=str(current_user.tenant_id),
            db_session=db,
        )
    except SubmissionReadinessEngineError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "/cases/{case_id}/submission-readiness/evidence",
    response_model=EvidenceBundle,
    status_code=status.HTTP_200_OK,
)
def get_submission_readiness_evidence(
    case_id: uuid.UUID,
    program_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Read-only evidence bundle for submission readiness (shadow, deterministic, audit-grade).
    """
    _require_admin_or_rcic(current_user)
    svc = SubmissionReadinessVerificationService()
    try:
        return svc.build_evidence_bundle(
            case_id=str(case_id),
            program_code=program_code,
            tenant_id=str(current_user.tenant_id),
            db_session=db,
        )
    except SubmissionReadinessEngineError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "/cases/{case_id}/submission-preparation",
    response_model=SubmissionPreparationPackage,
    status_code=status.HTTP_200_OK,
)
def get_submission_preparation_package(
    case_id: uuid.UUID,
    program_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deterministic, read-only submission preparation package (shadow-only).
    No submission is executed. RCIC/Admin/Owner only.
    """
    _require_admin_or_rcic(current_user)
    svc = SubmissionPreparationService()
    try:
        return svc.build_package(
            case_id=str(case_id),
            program_code=program_code,
            tenant_id=str(current_user.tenant_id),
            db_session=db,
        )
    except (SubmissionPreparationServiceError, SubmissionReadinessEngineError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "/cases/{case_id}/assisted-drafts",
    response_model=AssistedDraftBundle,
    status_code=status.HTTP_200_OK,
)
def get_assisted_drafts(
    case_id: uuid.UUID,
    program_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Draft-only assisted automation outputs, gated by automation readiness and tenant policy.
    """
    _require_admin_or_rcic(current_user)
    svc = AssistedDraftService()
    try:
        return svc.build_drafts(
            case_id=str(case_id),
            tenant_id=str(current_user.tenant_id),
            program_code=program_code,
            db_session=db,
        )
    except AssistedDraftsError as exc:
        status_code = getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST)
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

