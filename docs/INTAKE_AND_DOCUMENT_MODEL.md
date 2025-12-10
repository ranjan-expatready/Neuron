# Intake & Document Model (Design, M6.1)

## Overview
- Defines the canonical, config-first intake/document/form model for Neuron.
- Models: canonical client data (“facts”), reusable fields, program-specific intake templates, document/form requirements, and the human+AI configuration workflow.
- Goals: config-first, reusable across programs, explainable, self-serve friendly; UI is schema-driven, not hard-coded per program.

## Canonical Data Model (Layer 0)
- Single canonical profile, independent of pathway; every fact is entered once and reused.
- Readers: rule engine/CRS, document matrix, form mapping, reporting, AI explainability.
- Shapes (illustrative, not exhaustive):
  - PersonProfile (personal info)
  - FamilyProfile (spouse, dependants)
  - EducationHistory[]
  - EmploymentHistory[]
  - LanguageTests[]
  - ProofOfFunds[]
  - ResidencyHistory[]
  - ImmigrationHistory[]
  - ProgramSelections[] / Case metadata

## Field Dictionary (Layer 1)
- Registry of reusable fields/questions; UI renders from schema.
- Core attributes (aligns to future YAML schema):
  - id (stable key, e.g., person.date_of_birth)
  - label
  - data_path (path into canonical model, e.g., profile.personal.date_of_birth)
  - type: string | number | boolean | date | enum | money | list | object
  - ui_control: text, textarea, select, radio, checkbox, date, file, etc.
  - options_ref (for enums)
  - validations (required, min/max, regex, min_age_years, etc.)
  - visibility_conditions (optional, for conditional questions)
  - group / section
  - help_text, tags (e.g., ["crs_core", "ee_only"])
- Adding a new field:
  - Extend canonical schema if needed.
  - Add a new field entry to the dictionary.
  - Optionally wire into templates, documents, and forms.
- UI is schema-driven; no per-program hard-coding.

## Intake Templates (Layer 2)
- Program/pathway-specific compositions of fields.
- Template attributes:
  - id, label
  - applicable_programs (e.g., ["EE_FSW"])
  - applicable_plans (e.g., ["pro", "enterprise"])
  - steps: id, label, fields: [field_ids...]
- Behavior:
  - Multiple programs reuse the same fields.
  - Self-serve portal requests template → renders steps/fields dynamically.
  - When a client has multiple cases, data reuses from the canonical model.

## Document Matrix (Layer 3)
- Documents are config entities with:
  - id, label, category (identity, financial, education, etc.)
  - required_for_programs
  - required_when conditions (based on field values or canonical data)
    - Examples: required if family.size > 1; skip if person.citizenship == "CANADA".
- Document checklist engine:
  - Reads canonical profile.
  - Applies program + field-based rules.
  - Returns required/optional documents.

## Form Mapping (Layer 4)
- Forms (e.g., IMM0008) defined with:
  - id, label
  - applicable_programs
  - field_mappings: form field → canonical data_path or field ID.
- Notes:
  - Logical data maps to forms; PDF export/auto-fill is a later implementation detail.

## Self-Serve Portal / Client Flow
1) Client/case chooses program(s).
2) Backend returns an intake template for that program.
3) Frontend renders fields dynamically and saves into the canonical model.
4) Backend returns document checklist derived from the document matrix.
5) Frontend shows upload slots for documents.
6) Forms are generated/future-filled based on mappings.
- Mobile vs. web is just rendering; same configs drive both.

## Human + AI Config Governance
- Config entries (fields, templates, documents, forms) are:
  - Versioned; status: draft | in_review | active | retired.
  - Carry created_by, approved_by, created_at, approved_at.
- AI agents can propose new entries into draft (e.g., from new IRCC PDFs) and write into a proposed config or dedicated changes table.
- Humans review via Admin Config UI; approve → status becomes active; reject → status rejected with notes.
- Invariant: No new intake/doc/form config becomes active for production cases until a human has reviewed and approved it.

## Extensibility & New Fields
- Adding a new section (e.g., Family profile): extend canonical schema, add grouped fields, reuse in templates.
- Adding a new field (dropdown/text/numeric): add to dictionary, include validations (min/max, regex, length), wire into templates/doc rules/forms as needed.
- Validations are config-defined; frontend renderer enforces; backend validates canonical model against config.
- Frontend is a config-driven renderer consuming these schemas.

## Roadmap Linkage
- M6.1 — This doc + config stubs (fields, intake_templates, documents, forms).
- M6.2 — Backend loader/validator + checklist/intake APIs.
- M6.3 — Portal wiring: schema-driven UI rendering from configs.
- Later — Agent-powered config proposals based on IRCC PDFs and form diffs; admin approval workflows.

