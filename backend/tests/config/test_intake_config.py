from src.app.config.intake_config import (
    MissingReferenceError,
    clear_intake_config_cache,
    load_intake_bundle,
)


def test_load_intake_bundle_valid():
    clear_intake_config_cache()
    bundle = load_intake_bundle()
    assert bundle.fields
    assert bundle.templates
    assert bundle.documents
    assert bundle.forms
    field_ids = {f.id for f in bundle.fields}
    for tpl in bundle.templates:
        for step in tpl.steps:
            assert set(step.fields).issubset(field_ids)


def test_documents_reference_known_fields():
    clear_intake_config_cache()
    bundle = load_intake_bundle()
    valid_targets = {f.id for f in bundle.fields}.union({f.data_path for f in bundle.fields})
    for doc in bundle.documents:
        for cond in doc.required_when:
            assert cond.field in valid_targets


def test_invalid_reference_raises(monkeypatch, tmp_path):
    # Write a broken template referencing unknown field
    base = tmp_path
    (base / "fields.yaml").write_text("fields:\n  - id: a\n    label: A\n    data_path: a\n    type: string\n")
    (base / "intake_templates.yaml").write_text(
        "intake_templates:\n  - id: t1\n    label: T1\n    applicable_programs: [EE_FSW]\n    steps:\n      - id: s1\n        label: Step\n        fields: [missing_field]\n"
    )
    (base / "documents.yaml").write_text("document_definitions: []\n")
    (base / "forms.yaml").write_text("form_definitions: []\n")
    clear_intake_config_cache()
    try:
        load_intake_bundle(base)
        assert False, "expected MissingReferenceError"
    except MissingReferenceError:
        pass

