from datetime import date, timedelta

from src.app.cases.model import CaseService
from src.app.documents.service import DocumentMatrixService
from src.app.domain_config.service import ConfigService
from src.app.rules.models import CandidateProfile, EducationRecord, LanguageTestResult, WorkExperienceRecord
from src.app.services.rule_engine_service import RuleEngineService


def _eligible_profile() -> CandidateProfile:
    today = date.today()
    return CandidateProfile(
        marital_status="single",
        family_size=1,
        education=[EducationRecord(level="bachelor")],
        language_tests=[
            LanguageTestResult(
                test_type="IELTS",
                listening_clb=9,
                reading_clb=9,
                writing_clb=9,
                speaking_clb=9,
                expiry_date=today + timedelta(days=365),
            )
        ],
        work_experience=[
            WorkExperienceRecord(
                teer_level=1,
                start_date=today - timedelta(days=365),
                end_date=today,
                is_continuous=True,
                is_canadian=True,
            )
        ],
    )


def test_case_service_builds_case_with_docs_and_forms() -> None:
    cfg_service = ConfigService()
    rule_service = RuleEngineService(config_service=cfg_service)
    doc_service = DocumentMatrixService(config_service=cfg_service)
    case_service = CaseService(rule_engine=rule_service, document_service=doc_service)

    profile = _eligible_profile()
    case = case_service.build_case(profile)

    assert case.selected_program in ("CEC", "FSW", "FST")
    assert case.program_eligibility is not None
    assert len(case.required_forms) > 0
    assert any(doc.id == "passport" for doc in case.required_documents)

