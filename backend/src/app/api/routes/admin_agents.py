from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_current_user, get_db
from src.app.models.user import User
from src.app.schemas.agent import AgentActionResponse, AgentSessionResponse
from src.app.security.errors import ForbiddenError, TenantAccessError
from src.app.services.agent_orchestrator import AgentOrchestratorService
from src.app.agents.document_reviewer_agent import DocumentReviewerAgent
from src.app.services.intake_engine import IntakeEngine
from src.app.services.document_content_service import DocumentContentService

router = APIRouter()


def _require_admin_or_rcic(user: User):
    if not user.tenant_id:
        raise TenantAccessError("Tenant context required")
    if user.role not in ("admin", "owner", "rcic", "rcic_admin"):
        raise ForbiddenError("Agent logs require admin/RCIC access")


class DocumentReviewRequest(BaseModel):
    case_id: uuid.UUID
    program_code: Optional[str] = None


class DocumentReviewResponse(BaseModel):
    program_code: str
    case_id: str
    findings: dict
    agent_action_id: str
    agent_session_id: str


@router.get("/actions", response_model=List[AgentActionResponse])
async def list_agent_actions(
    case_id: Optional[str] = Query(None),
    agent_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin_or_rcic(current_user)
    service = AgentOrchestratorService(db)
    actions = service.fetch_actions(
        tenant_id=current_user.tenant_id, case_id=case_id, agent_name=agent_name, status=status
    )
    return [AgentActionResponse.model_validate(a) for a in actions]


@router.get("/sessions/{session_id}", response_model=AgentSessionResponse)
async def get_agent_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin_or_rcic(current_user)
    service = AgentOrchestratorService(db)
    result = service.fetch_session_with_actions(session_id, tenant_id=current_user.tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    session, actions = result
    base = AgentSessionResponse.model_validate(session)
    return base.model_copy(update={"actions": [AgentActionResponse.model_validate(a) for a in actions]})


@router.post("/document-review", response_model=DocumentReviewResponse)
async def run_document_review(
    payload: DocumentReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin_or_rcic(current_user)
    orchestrator = AgentOrchestratorService(db)
    intake_engine = IntakeEngine()
    content_service = DocumentContentService()
    agent = DocumentReviewerAgent(
        orchestrator=orchestrator,
        intake_engine=intake_engine,
        content_service=content_service,
    )
    try:
        result = agent.review_case(
            case_id=str(payload.case_id),
            tenant_id=str(current_user.tenant_id),
            db_session=db,
            program_code=payload.program_code,
            created_by_user_id=str(current_user.id),
        )
    except ValueError:
        empty = {
            "program_code": payload.program_code or "",
            "case_id": str(payload.case_id),
            "findings": {
                "required_present": [],
                "required_missing": [],
                "optional_present": [],
                "duplicates": [],
                "unmatched": [],
                "content_warnings": [],
                "quality_warnings": [],
            },
            "agent_action_id": "",
            "agent_session_id": "",
        }
        return DocumentReviewResponse(**empty)
    return DocumentReviewResponse(**result)

