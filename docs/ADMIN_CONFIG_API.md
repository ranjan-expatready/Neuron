# Admin Config Read API (DRAFT)

> Read-only introspection for domain configuration. No writes/updates. All values come from `config/domain/*.yaml` via `ConfigService` and `DocumentMatrixService`. Not legal advice.

## Purpose
- Provide human admins and AI config agents with a transparent view of the loaded domain configs (CRS, language, work experience, proof of funds, program rules, arranged employment, biometrics/medicals, documents, forms).
- Keep config-first governance: no hard-coded IRCC constants in code; everything is surfaced from YAML.
- Security (M4.3): endpoints require authentication; only admin/owner roles may access; responses are tenant-aware where applicable.
- Security (M4.3): endpoints require authentication; only admin/owner roles may access; responses are tenant-aware where applicable.

## Endpoints
- `GET /api/v1/admin/config`
  - Returns the full `DomainConfigSnapshot` (CRS, language, work_experience, proof_of_funds, program_rules, arranged_employment, biometrics_medicals, documents, forms, clb_tables, crs_transferability).
- `GET /api/v1/admin/config/sections`
  - Returns the list of available sections.
- `GET /api/v1/admin/config/{section_name}`
  - Returns a specific section by name.
  - 404 if the section is not found.

## Implementation Notes
- Router: `backend/src/app/api/routes/admin_config.py`
- Service: `backend/src/app/admin_config/service.py`
- Config loaders:
  - Domain rules via `ConfigService` → `config/domain/*.yaml`
  - Documents/forms via `DocumentMatrixService` → `config/domain/documents.yaml`, `config/domain/forms.yaml`
- Response models are Pydantic; everything is read-only for inspection.

## Usage
- For transparency/explainability dashboards.
- For future AI Config Agent to diff/validate active domain rules.
- Do **not** use for writes; add separate admin tooling for config edits.

## Tests
- `backend/tests/unit/api/test_admin_config.py`
- Run: `cd backend && pytest backend/tests/unit/api/test_admin_config.py`


> Security/Observability (M4.4): endpoints require authenticated users; logs carry request_id and tenant/user IDs; soft-deleted items stay hidden by default; internal health/metrics endpoints exist at /internal/healthz, /internal/readyz, /internal/metrics.
