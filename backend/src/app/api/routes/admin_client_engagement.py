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


def _build_agent(db: Session) -> ClientEngagementAgent:
    orchestrator = AgentOrchestratorService(db)
    case_repo = CaseRepository(db)
    return ClientEngagementAgent(orchestrator=orchestrator, case_repo=case_repo)


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

