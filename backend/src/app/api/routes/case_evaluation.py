from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.app.cases.history_service import CaseHistoryResult, CaseHistoryService
from src.app.cases.model import CaseService
from src.app.cases.repository import CaseRepository
from src.app.config.case_types_service import CaseTypeConfigError, CaseTypesConfigService
from src.app.config.plans_service import (
    PlanCaseTypeNotAllowed,
    PlanFeatureDisabled,
    PlanQuotaExceeded,
    PlansConfigService,
)
from src.app.db.database import get_db
from src.app.documents.service import DocumentMatrixService
from src.app.domain_config.service import ConfigService
from src.app.models.tenant import Tenant
from src.app.rules.models import CandidateProfile, ProgramEligibilityResult
from src.app.services.rule_engine_service import RuleEngineService


router = APIRouter()


class FactorDetail(BaseModel):
    name: str
    points: int
    rule_id: str
    config_ref: str | None = None


class CrsBreakdownResponse(BaseModel):
    total: int
    breakdown: dict[str, int] = Field(default_factory=dict)
    factor_details: list[FactorDetail] = Field(default_factory=list)


class ProgramEligibilityResponse(BaseModel):
    program_code: str
    eligible: bool
    reasons: list[str] = Field(default_factory=list)
    rule_ids: list[str] = Field(default_factory=list)


class DocumentRequirement(BaseModel):
    id: str
    label: str | None = None
    category: str | None = None
    mandatory: bool = True
    programs_applicable: list[str] = Field(default_factory=list)
    rule_ids: list[str] = Field(default_factory=list)


class AuditInfo(BaseModel):
    created_at: datetime
    source: str
    tenant_id: str
    case_type: str


class CaseEvaluationResponse(BaseModel):
    case_id: str
    version: int
    profile: CandidateProfile
    program_eligibility: list[ProgramEligibilityResponse]
    crs: CrsBreakdownResponse
    documents_and_forms: dict[str, list]
    required_artifacts: dict[str, list]
    config_version: dict[str, str]
    config: dict[str, str] | None = None
    warnings: list[str] = Field(default_factory=list)
    audit: AuditInfo
    tenant_id: str
    case_type: str


class CaseEvaluationRequest(BaseModel):
    profile: CandidateProfile
    tenant_id: str
    user_id: str
    case_type: str


def _config_hashes() -> dict[str, str]:
    files = [
        "config/domain/crs.yaml",
        "config/domain/programs.yaml",
        "config/domain/language.yaml",
        "config/domain/work_experience.yaml",
        "config/domain/proof_of_funds.yaml",
        "config/domain/arranged_employment.yaml",
        "config/domain/biometrics_medicals.yaml",
        "config/domain/forms.yaml",
        "config/domain/documents.yaml",
    ]
    hashes: dict[str, str] = {}
    for rel in files:
        path = Path(__file__).resolve().parents[4] / rel
        try:
            data = path.read_bytes()
            hashes[rel] = hashlib.sha256(data).hexdigest()
        except FileNotFoundError:
            hashes[rel] = "missing"
    return hashes


def _program_response(result: ProgramEligibilityResult) -> ProgramEligibilityResponse:
    return ProgramEligibilityResponse(
        program_code=result.program_code,
        eligible=result.eligible,
        reasons=result.reasons,
        rule_ids=[],
    )


def _persist_history(
    *,
    history_service: CaseHistoryService,
    profile: CandidateProfile,
    program_results: list[ProgramEligibilityResponse],
    crs_payload: dict[str, Any],
    required_artifacts: dict[str, list],
    config_fingerprint: dict[str, str],
    source: str,
    tenant_id: str,
    user_id: str,
    case_type: str,
) -> CaseHistoryResult:
    program_payload = [res.model_dump(mode="json") for res in program_results]
    return history_service.persist_evaluation(
        profile=profile.model_dump(mode="json"),
        program_eligibility={"results": program_payload},
        crs_breakdown=crs_payload,
        required_artifacts=required_artifacts,
        config_fingerprint=config_fingerprint,
        source=source,
        actor="system",
        tenant_id=tenant_id,
        created_by_user_id=user_id,
        case_type=case_type,
    )


@router.post("/evaluate", response_model=CaseEvaluationResponse)
async def evaluate_case(
    request: CaseEvaluationRequest, db: Session = Depends(get_db)
) -> CaseEvaluationResponse:
    config_service = ConfigService()
    rule_engine = RuleEngineService(config_service=config_service)
    document_service = DocumentMatrixService(config_service=config_service)
    case_service = CaseService(rule_engine=rule_engine, document_service=document_service)
    history_service = CaseHistoryService(db)
    plans_service = PlansConfigService()
    case_types_service = CaseTypesConfigService()
    case_repo = CaseRepository(db)

    tenant = db.query(Tenant).filter(Tenant.id == request.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    try:
        plan = plans_service.get_plan(tenant.plan_code)
        case_types_service.require_case_type(request.case_type)
        plans_service.assert_feature(plan, "enable_case_history")
        plans_service.assert_case_type_allowed(plan, request.case_type)
        active_cases = case_repo.count_active_cases(request.tenant_id)
        plans_service.assert_active_case_quota(plan, active_cases)
    except PlanFeatureDisabled as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except PlanCaseTypeNotAllowed as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PlanQuotaExceeded as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except CaseTypeConfigError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    case = case_service.build_case(request.profile)
    crs_results = rule_engine.evaluate(request.profile)
    crs_for_program = None
    if case.selected_program and case.selected_program in crs_results:
        crs_for_program = crs_results[case.selected_program].crs
    else:
        crs_for_program = next(iter(crs_results.values())).crs if crs_results else None

    crs_breakdown: dict[str, int] = {}
    factor_details: list[FactorDetail] = []
    total = 0
    if crs_for_program:
        crs_breakdown = {
            "core_points": crs_for_program.core_points,
            "spouse_points": crs_for_program.spouse_points,
            "transferability_points": crs_for_program.transferability_points,
            "additional_points": crs_for_program.additional_points,
        }
        total = crs_for_program.total_points
        factor_details = [
            FactorDetail(
                name="core_points",
                points=crs_for_program.core_points,
                rule_id="crs.core",
                config_ref="config/domain/crs.yaml",
            ),
            FactorDetail(
                name="spouse_points",
                points=crs_for_program.spouse_points,
                rule_id="crs.spouse",
                config_ref="config/domain/crs.yaml",
            ),
            FactorDetail(
                name="transferability_points",
                points=crs_for_program.transferability_points,
                rule_id="crs.transferability",
                config_ref="config/domain/crs.yaml",
            ),
            FactorDetail(
                name="additional_points",
                points=crs_for_program.additional_points,
                rule_id="crs.additional",
                config_ref="config/domain/crs.yaml",
            ),
        ]

    documents = [
        DocumentRequirement(
            id=d.id,
            label=getattr(d, "label", None),
            category=getattr(d, "category", None),
            mandatory=d.mandatory,
            programs_applicable=[case.selected_program] if case.selected_program else [],
            rule_ids=[],
        )
        for d in case.required_documents
    ]
    docs_payload = {
        "forms": list(case.required_forms),
        "documents": [doc.model_dump() for doc in documents],
    }

    warnings: list[str] = []
    if case.program_eligibility:
        for res in case.program_eligibility.results:
            warnings.extend(res.warnings)

    program_responses = (
        [_program_response(res) for res in case.program_eligibility.results]
        if case.program_eligibility
        else []
    )
    crs_payload = {
        "total": total,
        "breakdown": crs_breakdown,
        "factor_details": [fd.model_dump() for fd in factor_details],
    }
    config_version = _config_hashes()
    source = "express_entry_intake"

    history = _persist_history(
        history_service=history_service,
        profile=request.profile,
        program_results=program_responses,
        crs_payload=crs_payload,
        required_artifacts=docs_payload,
        config_fingerprint=config_version,
        source=source,
        tenant_id=request.tenant_id,
        user_id=request.user_id,
        case_type=request.case_type,
    )

    return CaseEvaluationResponse(
        case_id=history.case_id,
        version=history.version,
        profile=request.profile,
        program_eligibility=program_responses,
        crs=CrsBreakdownResponse(
            total=total,
            breakdown=crs_breakdown,
            factor_details=factor_details,
        ),
        documents_and_forms=docs_payload,
        required_artifacts=docs_payload,
        config_version=config_version,
        config=config_version,
        warnings=warnings,
        audit=AuditInfo(
            created_at=history.created_at,
            source=history.source,
            tenant_id=request.tenant_id,
            case_type=request.case_type,
        ),
        tenant_id=request.tenant_id,
        case_type=request.case_type,
    )

