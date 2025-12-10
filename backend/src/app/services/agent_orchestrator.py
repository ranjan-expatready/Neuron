from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from src.app.models.agent import AgentAction, AgentSession


class AgentOrchestratorService:
    """
    Minimal orchestration layer for agent sessions and actions.
    This is persistence-only in M8.0: no external calls or automation.
    """

    def __init__(self, db: Session):
        self.db = db

    # Sessions
    def create_session(
        self,
        agent_name: str,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        created_by_user_id: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> AgentSession:
        session = AgentSession(
            agent_name=agent_name,
            tenant_id=tenant_id,
            case_id=case_id,
            created_by_user_id=created_by_user_id,
            context=context or {},
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def close_session(self, session_id: str, status: str = "closed") -> Optional[AgentSession]:
        session = self.db.query(AgentSession).filter(AgentSession.id == session_id).first()
        if not session:
            return None
        session.status = status
        session.closed_at = session.closed_at or datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        return session

    # Actions
    def record_action(
        self,
        agent_name: str,
        action_type: str,
        payload: dict,
        status: str = "suggested",
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        session_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> AgentAction:
        action = AgentAction(
            agent_name=agent_name,
            action_type=action_type,
            payload=payload or {},
            status=status,
            tenant_id=tenant_id,
            case_id=case_id,
            session_id=session_id,
            error_message=error_message,
        )
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action

    def fetch_actions_for_case(
        self, case_id: str, tenant_id: Optional[str] = None, agent_name: Optional[str] = None, status: Optional[str] = None
    ) -> List[AgentAction]:
        query = self.db.query(AgentAction).filter(AgentAction.case_id == case_id)
        if tenant_id:
            query = query.filter(AgentAction.tenant_id == tenant_id)
        if agent_name:
            query = query.filter(AgentAction.agent_name == agent_name)
        if status:
            query = query.filter(AgentAction.status == status)
        return query.order_by(AgentAction.created_at.desc()).all()

    def fetch_actions(
        self,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[AgentAction]:
        query = self.db.query(AgentAction)
        if tenant_id:
            query = query.filter(AgentAction.tenant_id == tenant_id)
        if case_id:
            query = query.filter(AgentAction.case_id == case_id)
        if agent_name:
            query = query.filter(AgentAction.agent_name == agent_name)
        if status:
            query = query.filter(AgentAction.status == status)
        return query.order_by(AgentAction.created_at.desc()).all()

    def fetch_session_with_actions(self, session_id: str, tenant_id: Optional[str] = None) -> Optional[tuple[AgentSession, List[AgentAction]]]:
        session = self.db.query(AgentSession).filter(AgentSession.id == session_id).first()
        if not session:
            return None
        if tenant_id and session.tenant_id and session.tenant_id != tenant_id:
            return None
        actions_query = self.db.query(AgentAction).filter(AgentAction.session_id == session_id)
        if tenant_id:
            actions_query = actions_query.filter(AgentAction.tenant_id == tenant_id)
        actions = actions_query.order_by(AgentAction.created_at.desc()).all()
        return session, actions

