from __future__ import annotations

from typing import Dict

from src.app.services.agent_orchestrator import AgentOrchestratorService


class ClientEngagementAgent:
    """
    Suggestion-only agent for client engagement.
    No outbound messages or LLM calls in M8.0.
    """

    AGENT_NAME = "client_engagement"

    def __init__(self, orchestrator: AgentOrchestratorService):
        self.orchestrator = orchestrator

    def suggest_intake_reminder(self, case_id: str, tenant_id: str | None = None) -> Dict:
        suggestion = {
            "type": "intake_reminder",
            "message": "Reminder: please complete your intake. This is a draft suggestion only.",
        }
        action = self.orchestrator.record_action(
            agent_name=self.AGENT_NAME,
            action_type="suggest_intake_reminder",
            payload=suggestion,
            status="suggested",
            tenant_id=tenant_id,
            case_id=case_id,
        )
        return {"suggestion": suggestion, "action_id": action.id}

    def suggest_missing_docs_reminder(self, case_id: str, tenant_id: str | None = None) -> Dict:
        suggestion = {
            "type": "missing_documents",
            "message": "Reminder: documents are missing or incomplete. Please upload the required items.",
        }
        action = self.orchestrator.record_action(
            agent_name=self.AGENT_NAME,
            action_type="suggest_missing_docs_reminder",
            payload=suggestion,
            status="suggested",
            tenant_id=tenant_id,
            case_id=case_id,
        )
        return {"suggestion": suggestion, "action_id": action.id}

    def suggest_reply_to_client_question(self, case_id: str, question_id: str, tenant_id: str | None = None) -> Dict:
        suggestion = {
            "type": "client_question",
            "question_id": question_id,
            "message": "Proposed reply: We are reviewing your question and will follow up shortly.",
        }
        action = self.orchestrator.record_action(
            agent_name=self.AGENT_NAME,
            action_type="suggest_reply_to_client_question",
            payload=suggestion,
            status="suggested",
            tenant_id=tenant_id,
            case_id=case_id,
        )
        return {"suggestion": suggestion, "action_id": action.id}

