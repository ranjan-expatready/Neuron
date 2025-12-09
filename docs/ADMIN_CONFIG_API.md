# Admin Config Read API (DRAFT)

> Read-only introspection for domain configuration. No writes/updates. All values come from `config/domain/*.yaml` via `ConfigService` and `DocumentMatrixService`. Not legal advice.

## Purpose
- Provide human admins and AI config agents with a transparent view of the loaded domain configs (CRS, language, work experience, proof of funds, program rules, arranged employment, biometrics/medicals, documents, forms).
- Keep config-first governance: no hard-coded IRCC constants in code; everything is surfaced from YAML.

## Endpoints
- `GET /api/v1/admin/config?tenant_id=...`
  - Returns the full `DomainConfigSnapshot` (CRS, language, work_experience, proof_of_funds, program_rules, arranged_employment, biometrics_medicals, documents, forms, clb_tables, crs_transferability).
- `GET /api/v1/admin/config/sections?tenant_id=...`
  - Returns the list of available sections.
- `GET /api/v1/admin/config/{section_name}?tenant_id=...`
  - Returns a specific section by name.
  - 404 if the section is not found.
- `GET /api/v1/admin/config/plans?tenant_id=...`
  - Returns the pricing/plan catalog from `config/plans.yaml`.
- `GET /api/v1/admin/config/case-types?tenant_id=...`
  - Returns the case-type catalog from `config/case_types.yaml`.

## Implementation Notes
- Router: `backend/src/app/api/routes/admin_config.py`
- Service: `backend/src/app/admin_config/service.py`
- Config loaders:
  - Domain rules via `ConfigService` → `config/domain/*.yaml`
  - Documents/forms via `DocumentMatrixService` → `config/domain/documents.yaml`, `config/domain/forms.yaml`
- Plans via `PlansConfigService` → `config/plans.yaml`
- Case types via `CaseTypesConfigService` → `config/case_types.yaml`
- Response models are Pydantic; everything is read-only for inspection.
- Plan gating: requires tenant plan feature `enable_admin_config`; 403 if disabled.

## Usage
- For transparency/explainability dashboards.
- For future AI Config Agent to diff/validate active domain rules.
- Do **not** use for writes; add separate admin tooling for config edits.

## Tests
- `backend/tests/unit/api/test_admin_config.py`
- Run: `cd backend && pytest backend/tests/unit/api/test_admin_config.py`

