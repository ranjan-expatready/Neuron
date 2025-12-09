# Case Evaluation API (DRAFT)

> Internal engineering reference. Not legal advice. Config-driven only; no hard-coded IRCC constants.

## Endpoint

- `POST /api/v1/cases/evaluate`
  - Input: `CaseEvaluationRequest` containing a `CandidateProfile` (language tests, work experience, education, funds, job offers, biometrics/medicals metadata).
  - Output: `CaseEvaluationResponse` with:
    - `program_eligibility`: list per program (FSW/CEC/FST), eligibility flag, reasons, rule_ids.
    - `crs`: total + breakdown (core, spouse, transferability, additional) with factor details and config refs.
    - `documents_and_forms`: required forms/documents resolved via DocumentMatrixService.
    - `config_version`: sha256 hashes of active configs (crs, programs, language, work, proof_of_funds, arranged_employment, biometrics_medicals, forms, documents).
    - `warnings`: expiries/flags surfaced by rule engine.

## Architecture

- Services:
  - `RuleEngineService` → program eligibility + CRS (config-driven via ConfigService).
  - `DocumentMatrixService` → forms/documents from `config/domain/forms.yaml` and `config/domain/documents.yaml`.
  - `CaseService` → assembles selected program, eligibility summary, required artifacts.
- Router:
  - `backend/src/app/api/routes/case_evaluation.py`
  - Registered under `/api/v1/cases` in `backend/src/app/main.py`.

## Explainability

- Reasons surfaced per program eligibility.
- Rule IDs included where available; CRS factor details reference `config/domain/crs.yaml`.
- Config hashes reported to tie responses to specific config versions.

## Notes

- All logic is DRAFT pending SME/legal validation.
- Extend the router/response to include PNP or ADRs in future milestones as configs mature.

