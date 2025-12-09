# Rule Engine Overview (DRAFT)

> Engineering-facing design for eligibility + CRS evaluation. Not legal advice. All values/configs are authoritative only when pulled from config/domain YAMLs backed by domain_knowledge; no hard-coded constants.

## 1) Introduction

- Purpose: Evaluate immigration eligibility and scoring (CRS, plus PNP add-ons later) in a deterministic, auditable, testable way.
- Drivers: Config-first; domain_knowledge provides human-readable source + test oracle; runtime reads from config/domain/\*.yaml (and tenant overrides) to avoid hard-coded rules.
- Goals: Multi-tenant, configurable, traceable; every decision should be explainable (rule id + reason).

## 2) Inputs & Outputs

- Inputs (normalized profile, not raw forms):
  - Personal: age, marital status, dependants.
  - Education: level, ECA details.
  - Work: NOC/TEER, Canadian vs foreign, dates, hours, continuity.
  - Language tests: CELPIP/IELTS/PTE/TEF/TCF + dates; CLB per skill.
  - Proof of funds: balance snapshots/evidence.
  - Job offers / arranged employment: LMIA/LMIA-exempt, TEER, duration, full-time/non-seasonal, employer data.
  - Biometrics/medicals: status/validity.
  - Nomination flags (PNP), relatives, French, Canadian study.
- Outputs (per program: FSW, CEC, FST, EE-aligned PNP, etc.):
  - Eligibility status: eligible / ineligible / needs review.
  - Reasons: per requirement with rule ids/explanations.
  - CRS breakdown object: core, spouse, transferability, additional, total.
  - Warnings/flags: expiring tests, expiring medicals/biometrics, funds validity, missing ADR items.

## 3) Architecture Layers (conceptual)

- Data Normalization Layer:
  - Convert intake → normalized domain model using domain_knowledge definitions + config/domain YAMLs; apply tenant overrides (config/tenants) if allowed.
- Domain Adapters:
  - Map normalized data to eligibility inputs (min CLB, work continuity, funds, job offer validity).
  - Map to CRS inputs (age bucket, CLB per skill, education level, Canadian/foreign work years, nomination flag).
- Rule Evaluators:
  - Program eligibility evaluators: FSW, CEC, FST, EE-aligned PNP (and future programs), driven by `config/domain/programs.yaml`, `language.yaml`, `work_experience.yaml`, `proof_of_funds.yaml`.
  - Document & Forms Matrix: resolves required forms/documents per program using `config/domain/forms.yaml` and `config/domain/documents.yaml`.
  - CRS scorer: uses CRS core + spouse + transferability + additional points tables (from config informed by domain_knowledge).
- Aggregator:
  - Produce `EvaluationResult` with eligibility per program, CRS breakdown, required forms/documents (via CaseService), warnings/edge cases, and traceable rule ids.

## 7) Case Evaluation API

- Endpoint: `POST /api/v1/cases/evaluate`
- Uses ConfigService → RuleEngineService (eligibility + CRS) → DocumentMatrixService → CaseService.
- Returns explainable payload: program eligibility (reasons), CRS breakdown, forms/documents, config hashes, warnings.
- See `docs/RULE_ENGINE_CASE_API.md` for details.

## 4) Config-First Principles

- No IRCC constants hard-coded in backend/frontend. All numeric thresholds/tables come from config/domain YAMLs, authored from domain_knowledge sources.
- Domain_knowledge: canonical documentation + test oracle.
- Runtime: validated loaders for `config/domain/*.yaml` (and tenant overrides) feeding the evaluators.
- Future: feature flags for staged rollouts; schemas for CRS and eligibility YAMLs will be defined before wiring.

## 5) Testing Strategy (high level)

- Snapshot-based unit tests: known profiles → expected eligibility + CRS breakdown.
- Golden edge cases: borderline ages, continuity gaps, TEER 4–5 rejection, expiring language/medical/biometrics, funds exemptions.
- Integration tests: end-to-end evaluation using domain_knowledge examples as fixtures; ensure traceability (rule ids + explanations).

## 6) Config-First Rules (ENG-RULE-002)

- All thresholds/point tables are loaded from `config/domain/*.yaml` into a typed `DomainRulesConfig`; RuleEngine never hard-codes IRCC constants.
- YAMLs are derived from domain_knowledge (raw/processed) and marked DRAFT until SME validation.
- Safe evolution flow: update YAML (with citations/comments), add/adjust tests, load via config loader, then wire into the engine; no direct Python constants.
