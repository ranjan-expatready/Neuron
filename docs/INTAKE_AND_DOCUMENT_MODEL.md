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

## Implementation Status
- M6.2 delivered: validated config loaders (fields, templates, documents, forms), intake schema API (`/api/v1/intake-schema`), and document checklist API (`/api/v1/document-checklist/{case_id}`).
- UI wiring remains future (M6.3+); configs stay the single source of truth.
- M6.3 delivered: RCIC intake UI renders steps/fields from `/api/v1/intake-schema`, saves intake data to case form data, and surfaces document checklist from `/api/v1/document-checklist/{case_id}`. Client self-serve/mobile will reuse the same schema in future milestones.
- M6.3h delivered: RCIC intake now reads/writes canonical profile via `/api/v1/cases/{case_id}/profile`; select fields resolve options from config-backed `/api/v1/intake-options`; document checklist shows upload status by cross-referencing case documents.
- M6.4 delivered: Client self-serve intake portal renders the same schema via `/api/v1/intake-schema`, reads/writes canonical profile through `/api/v1/cases/{case_id}/profile`, and shows a client-facing document checklist with upload status derived from `/api/v1/cases/{case_id}/documents`.
- M7.1 delivered: Admin Config Console (read-only) exposes field dictionary, intake templates, document rules, form mappings, and option sets via `/api/v1/admin/intake/*` and new admin UI pages under `/admin/config/intake`.
- M7.2 delivered: Draft/edit layer (non-live) for intake configs. New DB-backed drafts and admin APIs/UI allow creating/updating draft field/template/document/form entries. Runtime engine continues to use YAML as the active source; activation/approval will come in M7.3.
- M7.3 delivered: Approval + activation. Active drafts can be promoted to `active`, recorded with approver, and merged as overrides on top of YAML for runtime intake/document/form configs. `retired`/`rejected` drafts remain historical only.

