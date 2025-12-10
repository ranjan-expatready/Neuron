from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_current_user, get_db
from src.app.cases.repository import CaseRepository
from src.app.models.user import User
from src.app.services.agent_orchestrator import AgentOrchestratorService
from src.app.agents.client_engagement_agent import ClientEngagementAgent
from src.app.services.client_engagement_settings_service import ClientEngagementSettingsService
from src.app.services.client_engagement_auto_runner import ClientEngagementAutoRunner

router = APIRouter()


def _require_admin_or_rcic(user: User) -> None:
    if user.role not in ("admin", "owner", "rcic", "rcic_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin client engagement APIs require admin/owner/rcic role",
        )
    if not user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Tenant context required for client engagement agent"
        )


class CaseRequest(BaseModel):
    case_id: uuid.UUID = Field(..., description="Case identifier")


class QuestionRequest(CaseRequest):
    question_text: str = Field(..., min_length=3, description="Client question text")


class SettingsResponse(BaseModel):
    auto_intake_reminders_enabled: bool
    auto_missing_docs_reminders_enabled: bool
    min_days_between_intake_reminders: int
    min_days_between_docs_reminders: int


class SettingsUpdateRequest(BaseModel):
    auto_intake_reminders_enabled: Optional[bool] = Field(None)
    auto_missing_docs_reminders_enabled: Optional[bool] = Field(None)
    min_days_between_intake_reminders: Optional[int] = Field(None, ge=1, le=30)
    min_days_between_docs_reminders: Optional[int] = Field(None, ge=1, le=30)


class AutoRunRequest(BaseModel):
    scope: Optional[str] = Field("tenant", description="tenant or case")
    case_id: Optional[uuid.UUID] = None


def _build_agent(db: Session) -> ClientEngagementAgent:
    orchestrator = AgentOrchestratorService(db)
    case_repo = CaseRepository(db)
    return ClientEngagementAgent(orchestrator=orchestrator, case_repo=case_repo)


def _build_settings_service(db: Session) -> ClientEngagementSettingsService:
    return ClientEngagementSettingsService(db)


def _build_auto_runner(db: Session) -> ClientEngagementAutoRunner:
    orchestrator = AgentOrchestratorService(db)
    case_repo = CaseRepository(db)
    agent = ClientEngagementAgent(orchestrator=orchestrator, case_repo=case_repo)
    settings_svc = ClientEngagementSettingsService(db)
    return ClientEngagementAutoRunner(db=db, agent=agent, orchestrator=orchestrator, settings_service=settings_svc)


@router.post("/intake-reminder")
def create_intake_reminder_suggestion(
    payload: CaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin_or_rcic(current_user)
    agent = _build_agent(db)
    try:
        result = agent.suggest_intake_incomplete_reminder(
            case_id=str(payload.case_id), tenant_id=str(current_user.tenant_id), db_session=db
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return result


@router.post("/missing-docs-reminder")
def create_missing_docs_reminder_suggestion(
    payload: CaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin_or_rcic(current_user)
    agent = _build_agent(db)
    try:
        result = agent.suggest_missing_docs_reminder(
            case_id=str(payload.case_id), tenant_id=str(current_user.tenant_id), db_session=db
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return result


@router.post("/client-question-reply")
def create_client_question_reply_suggestion(
    payload: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin_or_rcic(current_user)
    agent = _build_agent(db)
    try:
        result = agent.suggest_client_question_reply(
            case_id=str(payload.case_id),
            tenant_id=str(current_user.tenant_id),
            question_text=payload.question_text,
            db_session=db,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return result


@router.get("/settings", response_model=SettingsResponse)
def get_client_engagement_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in ("admin", "owner", "rcic", "rcic_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant context required")
    svc = _build_settings_service(db)
    settings = svc.get_settings_for_tenant(current_user.tenant_id)
    return SettingsResponse(
        auto_intake_reminders_enabled=settings.auto_intake_reminders_enabled,
        auto_missing_docs_reminders_enabled=settings.auto_missing_docs_reminders_enabled,
        min_days_between_intake_reminders=settings.min_days_between_intake_reminders,
        min_days_between_docs_reminders=settings.min_days_between_docs_reminders,
    )


@router.patch("/settings", response_model=SettingsResponse)
def update_client_engagement_settings(
    payload: SettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in ("admin", "owner"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin/owner may update settings")
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant context required")
    svc = _build_settings_service(db)
    settings = svc.update_settings(
        current_user.tenant_id,
        auto_intake_reminders_enabled=payload.auto_intake_reminders_enabled,
        auto_missing_docs_reminders_enabled=payload.auto_missing_docs_reminders_enabled,
        min_days_between_intake_reminders=payload.min_days_between_intake_reminders,
        min_days_between_docs_reminders=payload.min_days_between_docs_reminders,
    )
    return SettingsResponse(
        auto_intake_reminders_enabled=settings.auto_intake_reminders_enabled,
        auto_missing_docs_reminders_enabled=settings.auto_missing_docs_reminders_enabled,
        min_days_between_intake_reminders=settings.min_days_between_intake_reminders,
        min_days_between_docs_reminders=settings.min_days_between_docs_reminders,
    )


@router.post("/auto-run")
def run_client_engagement_auto(
    payload: AutoRunRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in ("admin", "owner"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin/owner may trigger auto-run")
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant context required")
    runner = _build_auto_runner(db)
    try:
        if payload.scope == "case" and payload.case_id:
            result = runner.run_for_case(str(payload.case_id), tenant_id=current_user.tenant_id, db_session=db)
            return {"cases_processed": 1, "intake_reminders": 1 if result["intake_sent"] else 0, "docs_reminders": 1 if result["docs_sent"] else 0, "details": [result]}
        # default tenant scope
        return runner.run_for_tenant(current_user.tenant_id, db_session=db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

