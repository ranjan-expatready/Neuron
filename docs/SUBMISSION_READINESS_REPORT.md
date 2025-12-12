# Submission Readiness Report (M11.1)

## Purpose
- Provide a deterministic, read-only readiness assessment for a case + form bundle before submission.
- Highlight missing required fields/documents and items needing RCIC confirmation.
- No DB writes, no PDF/web automation, no OCR/LLM calls.

## Inputs
- Tenant-scoped case (canonical profile + case documents).
- Form configs: `forms.yaml`, `form_mappings.yaml`, `form_bundles.yaml`.
- Document matrix (config/domain/documents.yaml + domain rules via `ConfigService`).

## Core Models
- `ReadinessSeverity`: `info|warn|blocker`.
- `ReadinessCheckResult`: code, severity, message, optional field_id/data_path/document_code/form_id, suggested_fix, evidence (keys/paths only).
- `FormReadinessSummary`: per-form completion %, missing required fields/docs, checks.
- `SubmissionReadinessReport`: case_id, bundle_id, generated_at, overall_status (`READY|NEEDS_REVIEW|NOT_READY`), completion %, blockers/warnings counts, per-form summaries, missing_documents, notes.

## Engine Logic (SubmissionReadinessService)
1) Load bundle, forms, mappings (config-first). Validate bundle_id; tenant+case must exist.
2) Run `FormAutofillEngine.build_autofill_preview` for the target bundle/program (read-only).
3) For each required field in the bundle’s forms:
   - If missing → `BLOCKER:missing_required_field`.
   - If value present with notes/ambiguity → `WARN:needs_confirmation`.
4) Compute per-form and overall completion % (required fields only).
5) Document checklist: `DocumentMatrixService.get_required_documents(profile, program)` vs case documents → `BLOCKER:missing_required_document` for gaps.
6) Status: `NOT_READY` if any blockers; `NEEDS_REVIEW` if warnings only; else `READY`.
7) Notes include config/preview warnings; no PII in evidence.

## API Surface (backend-only, read-only)
- `GET /api/v1/cases/{case_id}/submission/readiness?bundle_id=...&program_code?=...`
  - Roles: admin/owner/rcic/rcic_admin; tenant-scoped.
  - 400 on invalid bundle/config errors; 404 on missing case; 403 on RBAC/tenant failure.
- `GET /api/v1/config/form-bundles` (read-only list for UI dropdowns; same RBAC).

## Out of Scope (M11.1)
- No PDF fill/export, no web automation, no submission actions.
- No DB mutations, no AgentActions logging, no LLM/OCR.
- Frontend UI is optional follow-up (M11.1b).

## Testing
- Unit: READY vs NEEDS_REVIEW vs NOT_READY (missing fields/docs, warn on notes).
- API: 200 happy path, 400 invalid bundle, 404 missing case, 403 forbidden.
- Coverage target ≥85% maintained.


