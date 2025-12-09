# Case Types (M4.2)

## Overview
Case types are defined in `config/case_types.yaml` and describe supported workflows (Express Entry, Family Class, LMIA streams, etc.). Plans reference allowed case types to enforce gating.

## Schema (`config/case_types.yaml`)
- `code`: unique identifier (e.g., `express_entry_basic`, `family_class`)
- `label`: human-readable name
- `program_categories`: list of program categories the case type applies to
- `required_data_blocks`: required data sections to collect
- `required_documents`: required document/form categories

Example:
```
case_types:
  - code: express_entry_basic
    label: "Express Entry (Basic)"
    program_categories: [express_entry]
    required_data_blocks:
      - personal_info
      - language_tests
      - education
      - work_experience
      - proof_of_funds
    required_documents:
      - identity_documents
      - resume
```

## Runtime Usage
- Loaded via `CaseTypesConfigService`.
- Validation:
  - Case evaluation/history requires the requested `case_type` to exist.
  - Lifecycle operations ensure the case’s `case_type` is allowed by the tenant plan.
- `case_type` is persisted on `CaseRecord` and `CaseSnapshot` via migration `20251209_m42_pricing_case_types`.

## Admin APIs
- `GET /api/v1/admin/case-types?tenant_id=...` — returns the case-type catalog (requires admin_config feature on tenant plan).

## Frontend UX
- Intake flows and dashboards can display the selected case type and block unsupported case types per plan with a message: “This case type requires a higher plan.”

