# Rule Engine – CRS & Eligibility (DRAFT)

> Engineering-facing design for eligibility + CRS evaluation. Not legal advice. Values are sourced from domain_knowledge and runtime config/domain YAMLs; do not hard-code.

## 1) Scope

- Core Express Entry programs: FSW, CEC, FST (EE-aligned PNP builds on these).
- CRS scoring groups: core, spouse, transferability, additional.
- Uses: CLB tables, NOC/TEER mapping, arranged employment, proof of funds, biometrics/medicals validity.

## 2) Conceptual Data Model (sketch, no ORM)

- Candidate: personal, marital, dependants.
- EducationRecord: level, country, ECA status, completed_date.
- WorkExperienceRecord: country, noc_code, teer_level, start_date, end_date, hours_per_week, is_continuous, is_authorized (for Canadian), paid_flag.
- LanguageTestResult: test_type, test_date, scores per skill, clb_per_skill, expiry.
- ProofOfFundsSnapshot: amount, currency, as_of_date, evidence_refs.
- JobOffer (ArrangedEmployment): employer_id, noc_code, teer_level, has_lmia, lmia_exemption_code, full_time_flag, non_seasonal_flag, duration_months, location.
- MedicalStatus: status, exam_date, expiry_date.
- BiometricsStatus: status, collection_date, expiry_date.
- NominationFlag: province, nomination_date, is_enhanced, points = 600 (per CRS docs).

## 3) Rule Groups (overview)

- Eligibility (program gates):
  - FSW: CLB 7 all skills; ≥1 year continuous skilled work (TEER 0–3) in last 10 years; education with ECA; proof of funds unless exempt.
  - CEC: ≥1 year authorized skilled Canadian work in last 3 years; CLB 7 (TEER 0/1) or CLB 5 (TEER 2/3); funds generally not required.
  - FST: ≥2 years skilled trades work in last 5 years; job offer ≥1 year OR certificate of qualification; language min CLB 5 (speak/listen) / CLB 4 (read/write); funds unless exempt.
- CRS:
  - Core factors: age, education, first/second language, Canadian work.
  - Spouse factors: spouse education, language, Canadian work.
  - Transferability: education×language, education×Canadian work, foreign×language, foreign×Canadian work, certificate×language.
  - Additional: PNP (+600), French, study in Canada, siblings, possibly job-offer if re-enabled (currently removed per prior CRS doc).
  - Point values come from config/domain (to be defined); domain_knowledge raw tables remain the authoritative reference for tests.

## 4) Config-First Mapping (illustrative, not code)

```yaml
crs:
  core_factors:
    age:
      table_ref: "domain_knowledge/raw/crs/sources.md"
    language:
      clb_tables_ref: "domain_knowledge/raw/language/clb_tables.md"
  transferability:
    education_language:
      table_ref: "domain_knowledge/raw/crs/transferability_tables.md"
eligibility:
  fsw:
    min_clb: 7
    min_teer: [0, 1, 2, 3]
    require_continuous_months: 12
  cec:
    min_clb_teer_0_1: 7
    min_clb_teer_2_3: 5
    require_canadian_months: 12
  fst:
    min_clb_speak_listen: 5
    min_clb_read_write: 4
    require_trades_months: 24
    require_job_offer_or_certificate: true
```

- Runtime will read from config/domain YAMLs (future step). domain_knowledge is the human-readable source + test oracle.

## 5) Edge Cases & Flags

- Expiring/expired language tests, medicals, biometrics → warnings/blockers.
- Gaps vs continuous work; TEER 4/5 work (reject unless PNP override).
- Multiple language tests: pick best valid by date.
- Funds exemptions (CEC, valid job offer) vs required (FSW/FST).
- Draw type/category-based selection (future); keep hooks for program filters.

## 6) Traceability

- Every rule should have: `rule_id`, `rule_name`, `severity`, `explanation`, `source_ref` (domain_knowledge link).
- EvaluationResult should carry reason codes for eligibility decisions and CRS factor derivations to support audits and UI explanations.

## 7) Config Keys (ENG-RULE-002)

- Eligibility:
  - `language.yaml`: `fsw_min_clb`, `cec_min_clb_teer_0_1`, `cec_min_clb_teer_2_3`, `fst_min_clb_*`, `clb_tables_ref`.
  - `work_experience.yaml`: `eligible_teers`, `fsw.min_continuous_months`, `cec.min_canadian_months`, `cec.recency_years`.
  - `proof_of_funds.yaml`: `table[]`, `exemptions`.
  - `programs.yaml`: `program_rules[].uses_proof_of_funds`, `requires_job_offer`, `requires_certificate_or_offer`.
  - `arranged_employment.yaml`: `valid_teers`, `min_duration_months`, `require_full_time`, `require_non_seasonal`.
  - `biometrics_medicals.yaml`: `medical_validity_months`, `biometrics_validity_months`, `expiry_warning_days`.
- CRS:
  - `crs.yaml`: `crs_core.*` tables (age, education, first/second language, Canadian work), `crs_spouse.*` spouse factors, `crs_transferability.*` bundles + caps, `crs_additional.*` (PNP, sibling, French, Canadian study, job-offer toggles).
- Engine wiring:
  - YAMLs → `DomainRulesConfig` (config_models) via `config_loader.load_domain_rules_config()` → injected into `RuleEngine` / `RuleEngineService` and CRS engine.

## 8) M5.1 CRS Engine Core (config-first)
- Domain models: `backend/src/app/domain/crs/models.py` (`CRSProfileInput`, `CRSFactorContribution`, `CRSResult`).
- Engine: `backend/src/app/rules/crs_engine.py` computes core, spouse, transferability, additional points with per-factor rule references.
- Adapter: `backend/src/app/rules/crs_adapter.py` builds CRSProfileInput from CandidateProfile.
- Service wrapper: `backend/src/app/services/crs_engine.py` with structured logging (`component="crs_engine"`) and metrics counters (`crs_evaluations_total`, `crs_evaluations_failed_total`).
- Config source: `config/domain/crs.yaml` (tables derived from domain_knowledge/raw/crs/transferability_tables.md and Canada.ca CRS page, DRAFT until SME validation).

## 9) M5.2 Structured Explainability (no natural language yet)
- Each `CRSFactorContribution` now includes `explanation` with:
  - `explanation_code` (stable factor identifier)
  - `rule_path` (config path e.g., `crs_core.age_bands`, `crs_transferability.education_language`)
  - `input_summary` (normalized inputs used)
  - `threshold_summary` (key config thresholds/bands/caps)
- Explainability data is derived solely from `config/domain/crs.yaml`; no IRCC constants are coded.
- M5.3 will layer NL generation + UI; current output is machine-readable only.
