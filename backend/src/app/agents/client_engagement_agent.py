from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.app.cases.repository import CaseRepository
from src.app.services.agent_orchestrator import AgentOrchestratorService
from src.app.services.intake_engine import IntakeEngine, ResolvedField, _get_value


class ClientEngagementAgent:
    """
    Shadow-mode (suggest-only) client engagement agent.
    Deterministic, template-based suggestions; no outbound sends or LLM calls.
    """

    AGENT_NAME = "client_engagement"

    def __init__(
        self,
        orchestrator: AgentOrchestratorService,
        case_repo: CaseRepository,
        intake_engine: Optional[IntakeEngine] = None,
    ):
        self.orchestrator = orchestrator
        self.case_repo = case_repo
        self.intake_engine = intake_engine or IntakeEngine()

    # Utilities
    def _start_session(self, tenant_id: Optional[str], case_id: str) -> str:
        session = self.orchestrator.create_session(
            agent_name=self.AGENT_NAME, tenant_id=tenant_id, case_id=case_id
        )
        return session.id

    def _record_action(
        self,
        session_id: str,
        tenant_id: Optional[str],
        case_id: str,
        action_type: str,
        payload: dict,
    ):
        return self.orchestrator.record_action(
            agent_name=self.AGENT_NAME,
            action_type=action_type,
            payload=payload,
            status="suggested",
            tenant_id=tenant_id,
            case_id=case_id,
            session_id=session_id,
        )

    def _fetch_case(self, case_id: str, tenant_id: Optional[str]):
        case = self.case_repo.get_case(case_id, tenant_id=tenant_id)
        if not case:
            raise ValueError("Case not found or not accessible for tenant")
        return case

    def _infer_program(self, case) -> Optional[str]:
        return self.intake_engine._infer_program_from_case(case)  # pylint: disable=protected-access

    def _missing_sections(self, profile: Dict[str, Any], fields: List[ResolvedField]) -> List[str]:
        missing = []
        for field in fields:
            if field.required:
                val = _get_value(profile, field.data_path)  # pylint: disable=protected-access
                if val in (None, "", [], {}):
                    missing.append(field.label or field.id)
        return missing

    # Suggestions
    def suggest_intake_incomplete_reminder(
        self, case_id: str, tenant_id: Optional[str], db_session=None
    ) -> Dict[str, Any]:
        case = self._fetch_case(case_id, tenant_id)
        program_code = self._infer_program(case) or "unspecified_program"
        template = self.intake_engine.get_intake_schema_for_program(
            program_code=program_code, plan_code=None, db_session=db_session
        )

        missing_sections: List[str] = []
        profile = case.profile or {}
        for step in template.steps:
            step_missing = self._missing_sections(profile, step.fields)
            if step_missing:
                missing_sections.append(step.label or step.id)

        subject = "Draft: Intake completion reminder"
        body_lines = [
            f"Hi there, this is a draft reminder to complete your intake for program {program_code}.",
            "Sections still needing attention:",
        ]
        body_lines.extend([f"- {section}" for section in missing_sections] or ["- (could not determine, please review)"])
        body_lines.append("Please review and send via approved channels. This draft is for RCIC review only.")
        body = "\n".join(body_lines)

        suggestion = {
            "message_type": "intake_incomplete_reminder",
            "channel": "email_and_in_app",
            "subject": subject,
            "body": body,
            "missing_sections": missing_sections,
            "cta_url": "<intake_portal_link_placeholder>",
            "risk_level": "low",
            "requires_approval": True,
        }

        session_id = self._start_session(tenant_id, case_id)
        action = self._record_action(
            session_id, tenant_id, case_id, "intake_incomplete_reminder_suggestion", suggestion
        )
        return {"suggestion": suggestion, "action_id": action.id}

    def suggest_missing_docs_reminder(
        self, case_id: str, tenant_id: Optional[str], db_session=None
    ) -> Dict[str, Any]:
        case = self._fetch_case(case_id, tenant_id)
        program_code = self._infer_program(case) or "unspecified_program"
        checklist = self.intake_engine.get_document_checklist_for_case(
            case, program_code=program_code, db_session=db_session
        )
        missing_docs = [doc.label for doc in checklist if doc.required]

        subject = "Draft: Missing documents reminder"
        body_lines = [
            "Hi there, this is a draft reminder about required documents that are still pending.",
            "Missing required documents:",
        ]
        body_lines.extend([f"- {doc}" for doc in missing_docs] or ["- (could not determine, please review)"])
        body_lines.append("Please review and send via approved channels. This draft is for RCIC review only.")
        body = "\n".join(body_lines)

        suggestion = {
            "message_type": "missing_documents_reminder",
            "channel": "email_and_in_app",
            "subject": subject,
            "body": body,
            "missing_documents": missing_docs,
            "cta_url": "<document_upload_link_placeholder>",
            "risk_level": "low",
            "requires_approval": True,
        }

        session_id = self._start_session(tenant_id, case_id)
        action = self._record_action(
            session_id, tenant_id, case_id, "missing_documents_reminder_suggestion", suggestion
        )
        return {"suggestion": suggestion, "action_id": action.id}

    def suggest_client_question_reply(
        self, case_id: str, tenant_id: Optional[str], question_text: str, db_session=None
    ) -> Dict[str, Any]:
        case = self._fetch_case(case_id, tenant_id)
        program_code = self._infer_program(case) or "unspecified_program"
        client_name = case.profile.get("client_name") if isinstance(case.profile, dict) else None
        greeting = f"Hi {client_name}," if client_name else "Hi,"
        body = (
            f"{greeting} this is a draft reply for RCIC review.\n\n"
            f"Your question: \"{question_text}\"\n\n"
            "Draft answer: Thank you for your question. Based on your program "
            f"({program_code}), we are reviewing your information and will provide a detailed response shortly. "
            "No legal advice is provided in this draft. An RCIC must review and confirm before sending."
        )

        suggestion = {
            "message_type": "client_question_reply",
            "channel": "in_app",
            "subject": "Draft reply to client question",
            "body": body,
            "original_question": question_text,
            "risk_level": "medium",
            "requires_approval": True,
        }

        session_id = self._start_session(tenant_id, case_id)
        action = self._record_action(
            session_id, tenant_id, case_id, "client_question_reply_suggestion", suggestion
        )
        return {"suggestion": suggestion, "action_id": action.id}
