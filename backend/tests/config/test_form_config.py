from pathlib import Path

import pytest

from src.app.config.form_config import (
    FormConfigError,
    MissingReferenceError,
    clear_caches,
    load_form_bundles,
    load_form_definitions,
    load_form_mappings,
)


@pytest.fixture(autouse=True)
def clear_cache_fixture():
    clear_caches()
    yield
    clear_caches()


def test_load_form_definitions_from_repo():
    forms = load_form_definitions()
    imm0008 = next(f for f in forms if f.id == "IMM0008")
    assert imm0008.version.startswith("v")
    assert imm0008.status in {"draft", "active", "retired"}
    assert any(field.field_id == "given_name" for field in imm0008.fields)


def test_load_form_mappings_valid():
    mappings = load_form_mappings()
    assert any(m.form_id == "IMM0008" for m in mappings)
    marital = next(m for m in mappings if m.id == "imm0008_marital_status")
    assert marital.source_type == "canonical_profile"
    assert marital.source_path.endswith("marital_status")


def test_invalid_mapping_field_id_raises(tmp_path: Path):
    base = tmp_path
    (base / "forms.yaml").write_text(
        """
form_definitions:
  - id: "F1"
    label: "Form 1"
    version: "v1"
    status: "active"
    type: "pdf"
    fields:
      - field_id: "a"
        label: "A"
        data_type: "text"
        required: true
""",
        encoding="utf-8",
    )
    (base / "form_mappings.yaml").write_text(
        """
form_field_mappings:
  - id: "m1"
    form_id: "F1"
    field_id: "missing_field"
    source_type: "canonical_profile"
    source_path: "profile.x"
    status: "draft"
""",
        encoding="utf-8",
    )
    with pytest.raises(MissingReferenceError):
        load_form_mappings(base_path=base)


def test_invalid_bundle_missing_form_raises(tmp_path: Path):
    base = tmp_path
    (base / "forms.yaml").write_text(
        """
form_definitions:
  - id: "F1"
    label: "Form 1"
    version: "v1"
    status: "active"
    type: "pdf"
    fields:
      - field_id: "a"
        label: "A"
        data_type: "text"
        required: true
""",
        encoding="utf-8",
    )
    (base / "form_mappings.yaml").write_text("form_field_mappings: []\n", encoding="utf-8")
    (base / "form_bundles.yaml").write_text(
        """
form_bundles:
  - id: "bundle1"
    label: "Bundle"
    program_codes: ["EE_FSW"]
    forms: ["F1", "MISSING"]
    status: "active"
""",
        encoding="utf-8",
    )
    with pytest.raises(MissingReferenceError):
        load_form_bundles(base_path=base)


def test_bundles_load_with_valid_refs():
    bundles = load_form_bundles()
    assert any(b.id == "ee_fsw_base_package" for b in bundles)


