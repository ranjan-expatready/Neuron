from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from src.app.documents.service import DocumentMatrixResult, DocumentMatrixService
from src.app.rules.models import CandidateProfile, ProgramEligibilitySummary
from src.app.services.rule_engine_service import RuleEngineService


class Case(BaseModel):
    profile: CandidateProfile
    program_eligibility: Optional[ProgramEligibilitySummary] = None
    selected_program: Optional[str] = None
    required_forms: List[str] = Field(default_factory=list)
    required_documents: List = Field(default_factory=list)


class CaseService:
    def __init__(self, rule_engine: RuleEngineService, document_service: DocumentMatrixService) -> None:
        self.rule_engine = rule_engine
        self.document_service = document_service

    def build_case(self, profile: CandidateProfile) -> Case:
        eligibility = self.rule_engine.evaluate_programs(profile)
        program = eligibility.primary_recommendation()

        docs = DocumentMatrixResult()
        if program:
            docs = self.document_service.get_required_documents(profile, program)

        return Case(
            profile=profile,
            program_eligibility=eligibility,
            selected_program=program,
            required_forms=docs.required_forms,
            required_documents=docs.required_documents,
        )


