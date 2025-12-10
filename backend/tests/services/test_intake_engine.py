from src.app.config.intake_config import clear_intake_config_cache
from src.app.services.intake_engine import IntakeEngine


def test_intake_schema_resolution():
    clear_intake_config_cache()
    engine = IntakeEngine()
    schema = engine.get_intake_schema_for_program("EE_FSW")
    assert schema.steps
    first_step = schema.steps[0]
    assert first_step.fields
    assert first_step.fields[0].id.startswith("person.")


def test_document_checklist_conditions():
    clear_intake_config_cache()
    engine = IntakeEngine()
    profile = {
        "profile": {
            "personal": {"citizenship": "INDIA"},
            "family": {"size": 3},
        }
    }
    checklist = engine.get_document_checklist_for_profile(profile, "EE_FSW")
    items = {item.id: item for item in checklist}
    assert items["passport_main"].required is True
    assert items["proof_of_funds"].required is True
    assert any("family.size" in reason for reason in items["proof_of_funds"].reasons)


def test_document_checklist_inferred_program():
    clear_intake_config_cache()
    engine = IntakeEngine()
    case = type(
        "CaseObj",
        (),
        {
            "profile": {"profile": {"family": {"size": 1}}},
            "program_eligibility": {"results": [{"program_code": "EE_FSW", "eligible": True}]},
        },
    )()
    checklist = engine.get_document_checklist_for_case(case)
    assert checklist

