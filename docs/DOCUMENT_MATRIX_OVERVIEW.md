# Document & Forms Matrix (DRAFT, Engineering View)

> Internal reference. Not legal advice. All requirements are config-driven from `config/domain/forms.yaml` and `config/domain/documents.yaml`.

## Purpose

- Centralize Express Entry (FSW/CEC/FST) forms and supporting document requirements.
- Keep document/form logic config-first for future admin tooling and tenant overrides.
- Feed downstream case assembly and submission readiness checks.

## Config Schema (draft)

- `config/domain/forms.yaml`
  - `forms.express_entry.<program_code>` → list of form IDs (e.g., IMM0008, IMM5669, IMM5406)
  - `forms.spouse` → spouse-related forms (e.g., IMM5406)
- `config/domain/documents.yaml`
  - `documents.<program_code>.base` → core docs for the program
  - `documents.<program_code>.spouse` → additional spouse docs
  - `documents.<program_code>.pof_required` → docs needed when proof of funds is required

## Service Architecture

- `DocumentMatrixService` (backend/src/app/documents/service.py)
  - Loads forms/documents YAML.
  - Reads DomainRulesConfig via ConfigService to decide PoF applicability.
  - Returns `DocumentMatrixResult` with required_forms and required_documents.
- `CaseService` (backend/src/app/cases/model.py)
  - Uses RuleEngineService for program eligibility (FSW/CEC/FST).
  - Uses DocumentMatrixService to fetch required forms/docs for the selected program.
  - Produces a `Case` skeleton with eligibility + required artifacts.

## Rule Ordering (current)

1) Determine program eligibility (RuleEngineService).
2) Choose primary program (CEC → FSW → FST heuristic).
3) Resolve documents/forms:
   - Base docs
   - Spouse docs if marital_status in {married, common-law}
   - Proof-of-funds docs if program uses PoF and not exempt in PoF config
4) Return structured result.

## Example (FSW, single)

- Forms: IMM0008, IMM5669
- Documents: passport, ECA report, language test, work experience letters, proof of funds

## Notes

- All content is DRAFT pending SME/legal validation.
- Extend YAML + service to add programs, ADR rules, or tenant overrides in future milestones.

