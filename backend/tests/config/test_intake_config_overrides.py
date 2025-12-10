import uuid

from src.app.config.intake_config import clear_intake_config_cache, load_intake_bundle
from src.app.models.intake_config_draft import IntakeConfigDraft


def _baseline(bundle):
    return {f.id: f.label for f in bundle.fields}


def test_no_active_overrides_uses_yaml_baseline(client):
    clear_intake_config_cache()
    baseline = load_intake_bundle(include_overrides=False)
    merged = load_intake_bundle(db_session=client.db_session)
    assert _baseline(merged) == _baseline(baseline)


def test_active_field_override_applied(client):
    clear_intake_config_cache()
    # choose an existing field id from YAML
    override = IntakeConfigDraft(
        config_type="field",
        key="person.date_of_birth",
        payload={
            "id": "person.date_of_birth",
            "label": "Date of Birth (Override)",
            "data_path": "profile.personal.date_of_birth",
            "type": "date",
            "ui_control": "date",
        },
        status="active",
        created_by="tester",
        updated_by="tester",
    )
    client.db_session.add(override)
    client.db_session.commit()

    merged = load_intake_bundle(db_session=client.db_session)
    field_lookup = {f.id: f.label for f in merged.fields}
    assert field_lookup["person.date_of_birth"] == "Date of Birth (Override)"


def test_retired_override_not_applied(client):
    clear_intake_config_cache()
    override = IntakeConfigDraft(
        config_type="field",
        key="person.date_of_birth",
        payload={
            "id": "person.date_of_birth",
            "label": "Should Not Apply",
            "data_path": "profile.personal.date_of_birth",
            "type": "date",
            "ui_control": "date",
        },
        status="retired",
        created_by="tester",
        updated_by="tester",
    )
    client.db_session.add(override)
    client.db_session.commit()

    merged = load_intake_bundle(db_session=client.db_session)
    field_lookup = {f.id: f.label for f in merged.fields}
    assert field_lookup.get("person.date_of_birth") != "Should Not Apply"

