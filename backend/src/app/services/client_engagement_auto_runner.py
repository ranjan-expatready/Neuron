from __future__ import annotations

import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy.orm import Session

from src.app.agents.client_engagement_agent import ClientEngagementAgent
from src.app.cases.repository import CaseRepository
from src.app.services.agent_orchestrator import AgentOrchestratorService
from src.app.services.client_engagement_settings_service import ClientEngagementSettingsService


class ClientEngagementAutoRunner:
    """
    Manual/externally-triggered AUTO runner (no internal cron).
    Handles low-risk reminders only (intake incomplete, missing docs).
    Logs executed actions with auto_mode=True.
    """

    def __init__(
        self,
        db: Session,
        agent: ClientEngagementAgent,
        orchestrator: AgentOrchestratorService,
        settings_service: ClientEngagementSettingsService,
    ):
        self.db = db
        self.agent = agent
        self.orchestrator = orchestrator
        self.settings_service = settings_service
        self.case_repo = CaseRepository(db)

    def _now(self) -> datetime.datetime:
        return datetime.datetime.utcnow()

    def _last_auto_action_time(self, case_id: str, tenant_id: str, action_type: str) -> Optional[datetime.datetime]:
        actions = self.orchestrator.fetch_actions(
            case_id=case_id, tenant_id=tenant_id, action_type=action_type, status="executed", auto_mode=True
        )
        if not actions:
            return None
        return actions[0].created_at

    def _throttled(self, last_time: Optional[datetime.datetime], min_days: int) -> bool:
        if not last_time:
            return False
        return (self._now() - last_time).days < min_days

    def _record_executed(self, tenant_id: str, case_id: str, action_type: str, suggestion: Dict[str, Any]):
        # mark as executed auto action
        self.orchestrator.record_action(
            agent_name=self.agent.AGENT_NAME,
            action_type=action_type,
            payload={**suggestion, "auto_mode": True, "send_status": "simulated"},
            status="executed",
            tenant_id=tenant_id,
            case_id=case_id,
            auto_mode=True,
        )

    def run_for_case(self, case_id: str, tenant_id: str, db_session=None) -> Dict[str, Any]:
        settings = self.settings_service.get_settings_for_tenant(tenant_id)
        summary = {"case_id": case_id, "intake_sent": False, "docs_sent": False}
        # intake reminder
        if settings.auto_intake_reminders_enabled:
            last_time = self._last_auto_action_time(case_id, tenant_id, "intake_incomplete_reminder_auto")
            if not self._throttled(last_time, settings.min_days_between_intake_reminders):
                suggestion = self.agent.suggest_intake_incomplete_reminder(
                    case_id, tenant_id=tenant_id, db_session=db_session, use_llm=False
                )["suggestion"]
                if suggestion.get("missing_sections"):
                    self._record_executed(tenant_id, case_id, "intake_incomplete_reminder_auto", suggestion)
                    summary["intake_sent"] = True
        # docs reminder
        if settings.auto_missing_docs_reminders_enabled:
            last_time = self._last_auto_action_time(case_id, tenant_id, "missing_documents_reminder_auto")
            if not self._throttled(last_time, settings.min_days_between_docs_reminders):
                suggestion = self.agent.suggest_missing_docs_reminder(
                    case_id, tenant_id=tenant_id, db_session=db_session, use_llm=False
                )["suggestion"]
                if suggestion.get("missing_documents"):
                    self._record_executed(tenant_id, case_id, "missing_documents_reminder_auto", suggestion)
                    summary["docs_sent"] = True
        return summary

    def run_for_tenant(self, tenant_id: str, limit_per_run: int = 50, db_session=None) -> Dict[str, Any]:
        cases = self.case_repo.list_recent(limit=limit_per_run, tenant_id=tenant_id)
        details: List[Dict[str, any]] = []
        intake_count = 0
        docs_count = 0
        for case in cases:
            result = self.run_for_case(case.id, tenant_id=tenant_id, db_session=db_session)
            intake_count += 1 if result["intake_sent"] else 0
            docs_count += 1 if result["docs_sent"] else 0
            if result["intake_sent"] or result["docs_sent"]:
                details.append(result)
        return {"cases_processed": len(cases), "intake_reminders": intake_count, "docs_reminders": docs_count, "details": details}

