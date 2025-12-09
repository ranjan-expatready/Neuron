from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.app.cases.model import CaseService
from src.app.documents.service import DocumentMatrixService
from src.app.domain_config.service import ConfigService
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


class CaseEvaluationResponse(BaseModel):
    program_eligibility: list[ProgramEligibilityResponse]
    crs: CrsBreakdownResponse
    documents_and_forms: dict[str, list]
    config_version: dict[str, str]
    warnings: list[str] = Field(default_factory=list)


class CaseEvaluationRequest(BaseModel):
    profile: CandidateProfile


def _config_hashes() -> dict[str, str]:
    import hashlib
    from pathlib import Path

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


@router.post("/evaluate", response_model=CaseEvaluationResponse)
async def evaluate_case(request: CaseEvaluationRequest) -> CaseEvaluationResponse:
    config_service = ConfigService()
    rule_engine = RuleEngineService(config_service=config_service)
    document_service = DocumentMatrixService(config_service=config_service)
    case_service = CaseService(rule_engine=rule_engine, document_service=document_service)

    case = case_service.build_case(request.profile)
    crs_results = rule_engine.evaluate(request.profile)
    crs_for_program = None
    if case.selected_program and case.selected_program in crs_results:
        crs_for_program = crs_results[case.selected_program].crs
    else:
        crs_for_program = next(iter(crs_results.values())).crs if crs_results else None

    crs_breakdown = {}
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

    docs = {
        "forms": case.required_forms,
        "documents": [
            DocumentRequirement(
                id=d.id,
                label=getattr(d, "label", None),
                category=getattr(d, "category", None),
                mandatory=d.mandatory,
                programs_applicable=[case.selected_program] if case.selected_program else [],
                rule_ids=[],
            )
            for d in case.required_documents
        ],
    }

    warnings: list[str] = []
    if case.program_eligibility:
        for res in case.program_eligibility.results:
            warnings.extend(res.warnings)

    return CaseEvaluationResponse(
        program_eligibility=[
            _program_response(res) for res in case.program_eligibility.results
        ]
        if case.program_eligibility
        else [],
        crs=CrsBreakdownResponse(total=total, breakdown=crs_breakdown, factor_details=factor_details),
        documents_and_forms=docs,
        config_version=_config_hashes(),
        warnings=warnings,
    )
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.app.cases.model import CaseService
from src.app.documents.service import DocumentMatrixService
from src.app.domain_config.service import ConfigService
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


class CaseEvaluationResponse(BaseModel):
    program_eligibility: list[ProgramEligibilityResponse]
    crs: CrsBreakdownResponse
    documents_and_forms: dict[str, list]
    config_version: dict[str, str]
    warnings: list[str] = Field(default_factory=list)


class CaseEvaluationRequest(BaseModel):
    profile: CandidateProfile


def _config_hashes() -> dict[str, str]:
    import hashlib
    from pathlib import Path

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
    # We surface reasons; rule_ids can be extended later for granular flags.
    return ProgramEligibilityResponse(
        program_code=result.program_code,
        eligible=result.eligible,
        reasons=result.reasons,
        rule_ids=[],
    )


@router.post("/evaluate", response_model=CaseEvaluationResponse)
async def evaluate_case(request: CaseEvaluationRequest) -> CaseEvaluationResponse:
    config_service = ConfigService()
    rule_engine = RuleEngineService(config_service=config_service)
    document_service = DocumentMatrixService(config_service=config_service)
    case_service = CaseService(rule_engine=rule_engine, document_service=document_service)

    case = case_service.build_case(request.profile)
    # Use full profile evaluation to pick CRS breakdown
    crs_results = rule_engine.evaluate(request.profile)
    crs_for_program = None
    if case.selected_program and case.selected_program in crs_results:
        crs_for_program = crs_results[case.selected_program].crs
    else:
        crs_for_program = next(iter(crs_results.values())).crs if crs_results else None

    crs_breakdown = {}
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
            FactorDetail(name="core_points", points=crs_for_program.core_points, rule_id="crs.core", config_ref="config/domain/crs.yaml"),
            FactorDetail(name="spouse_points", points=crs_for_program.spouse_points, rule_id="crs.spouse", config_ref="config/domain/crs.yaml"),
            FactorDetail(name="transferability_points", points=crs_for_program.transferability_points, rule_id="crs.transferability", config_ref="config/domain/crs.yaml"),
            FactorDetail(name="additional_points", points=crs_for_program.additional_points, rule_id="crs.additional", config_ref="config/domain/crs.yaml"),
        ]

    docs = {
        "forms": case.required_forms,
        "documents": [
            DocumentRequirement(
                id=d.id,
                label=getattr(d, "label", None),
                category=getattr(d, "category", None),
                mandatory=d.mandatory,
                programs_applicable=[case.selected_program] if case.selected_program else [],
                rule_ids=[],
            )
            for d in case.required_documents
        ],
    }

    warnings: list[str] = []
    if case.program_eligibility:
        for res in case.program_eligibility.results:
            warnings.extend(res.warnings)

    return CaseEvaluationResponse(
        program_eligibility=[
            _program_response(res) for res in case.program_eligibility.results
        ]
        if case.program_eligibility
        else [],
        crs=CrsBreakdownResponse(total=total, breakdown=crs_breakdown, factor_details=factor_details),
        documents_and_forms=docs,
        config_version=_config_hashes(),
        warnings=warnings,
    )

