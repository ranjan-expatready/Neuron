# CRS Engine Overview (M5.1, DRAFT)

- Scope: Express Entry CRS (core human capital, spouse factors, skill transferability, additional points). PNP add-ons remain config-driven via `crs_additional.provincial_nomination`.
- Config-first: All points come from `config/domain/crs.yaml`; no IRCC constants in code. Tables mirror Canada.ca CRS criteria (date modified 2025-08-21) and are marked DRAFT pending SME validation.

## Inputs (CRSProfileInput)
- `age`, `marital_status`
- `education_level` (normalized enum matching config levels)
- `first_official_language` (CLB per skill), optional `second_official_language`
- `canadian_work_experience_years`, `foreign_work_experience_years`
- Optional spouse: `spouse_education_level`, `spouse_language`, `spouse_canadian_work_experience_years`
- Flags: `has_certificate_of_qualification`, `has_valid_job_offer`, `job_offer_teer_category`, `has_provincial_nomination`, `has_sibling_in_canada`, `canadian_study_years`, `first_language_is_french`

## Outputs (CRSResult)
- `total_score`
- `factor_contributions[]` each with:
  - `factor_code` (e.g., `core_human_capital_age`, `transferability_foreign_work_language`)
  - `points_awarded`, `points_max`
  - `inputs_used` (structured dict)
  - `rule_reference` (config key)

## Modules
- `backend/src/app/rules/crs_engine.py` — pure scorer using `DomainRulesConfig`.
- `backend/src/app/rules/crs_adapter.py` — builds `CRSProfileInput` from `CandidateProfile`.
- `backend/src/app/services/crs_engine.py` — service wrapper with structured logging + metrics.
- Domain models: `backend/src/app/domain/crs/models.py`.

## Config Sources
- `config/domain/crs.yaml` — age, education, language, Canadian work, spouse, transferability, additional points.
- Related refs: `config/domain/language.yaml`, `config/domain/work_experience.yaml`, `domain_knowledge/raw/crs/transferability_tables.md`.

## Explainability
- Each contribution carries rule_reference + inputs_used; downstream UI/agents can render structured factor breakdowns without new computation.

## Integration Notes
- Not yet wired into case evaluation API; use `CRSEngineService.compute_for_candidate` or `.compute_for_profile` for now.
- Observability: logs with `component="crs_engine"` and metrics counters `crs_evaluations_total` / `_failed_total`.

## Structured Explainability (M5.2)
- `CRSFactorContribution.explanation` is machine-readable (no natural language):
  - `explanation_code` – stable identifier per factor (e.g., `core.age.single`, `transferability.education_language`, `additional.provincial_nomination`).
  - `rule_path` – config path for the rule (e.g., `crs_core.age_bands`, `crs_transferability.education_language`, `crs_additional.french`).
  - `input_summary` – normalized inputs used (age, marital_status, education_level, CLB scores, work buckets, flags).
  - `threshold_summary` – key config values/bands applied (points, caps, min/max ranges).
  - `notes` – optional structured extras.
- All explanation data is derived from `config/domain/crs.yaml`; no IRCC constants appear in code.
- M5.3 will add natural-language generation + UI surfacing; current output stays structured-only.

## M5.3 – Natural-Language Explanations & Case Integration
- Added `CRSFactorNLExplanation` and optional `nl_explanation` on each `CRSFactorContribution` with titles/descriptions derived from structured explanations (no hard-coded IRCC constants).
- CRS engine service now enriches results with NL explanations via `crs_explanation_generator.py`.
- Case Evaluation API now returns CRS total, factor contributions, and explanations; case history snapshots store CRS payload (score + explanations) for audit.

