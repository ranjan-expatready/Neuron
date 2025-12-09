# Program Eligibility Engine (DRAFT, Engineering View)

> Internal reference for engineers. Not legal advice. All thresholds are config-driven from `config/domain/*.yaml`; no IRCC constants are hard-coded.

## Scope

- Express Entry programs: FSW, CEC, FST (hooks ready for EE-aligned PNP later).
- Consumes typed config via `ConfigService` → `DomainConfigBundle`.
- Returns structured `ProgramEligibilityResult` per program plus a `ProgramEligibilitySummary`.

## Inputs

- Candidate profile (`backend/src/app/rules/models.py`):
  - Language tests (CLB per skill)
  - Work experience (TEER, continuous, Canadian flag, dates)
  - Education records
  - Proof of funds snapshots
  - Job offers (LMIA/non-seasonal flags, duration)
  - Biometrics/medical are surfaced as flags via config if needed later
- Domain config (`config/domain/*.yaml`):
  - `programs.yaml` → program toggles, PoF usage, education notes, job-offer/cert requirements
  - `language.yaml` → program minima (FSW/CEC/FST CLB thresholds)
  - `work_experience.yaml` → eligible TEERs, min continuous/canadian months
  - `proof_of_funds.yaml` → thresholds + exemptions

## Outputs

- `ProgramEligibilityResult`:
  - `program_code`, `eligible`, `reasons`, `warnings`, `metadata`
- `ProgramEligibilitySummary`:
  - List of results
  - Helpers: `eligible_programs()`, `primary_recommendation()` (simple priority: CEC → FSW → FST)
- Downstream usage:
  - DocumentMatrixService consumes selected program to resolve forms/documents.
  - CaseService assembles program eligibility + required forms/documents into a case skeleton.

## Rule Outline (config-driven)

- **FSW**
  - Language: `language.fsw_min_clb`
  - Work: continuous skilled months per `work_experience.fsw.min_continuous_months` + `eligible_teers`
  - Education: presence check (config field `min_education_level`, future expansion)
  - Funds: `proof_of_funds` unless exempt
- **CEC**
  - Canadian work: `work_experience.cec.min_canadian_months`, `recency_years`
  - Language: `language.cec_min_clb_teer_0_1` vs `language.cec_min_clb_teer_2_3`
  - Funds: only if config says `uses_proof_of_funds`
- **FST**
  - Language: `language.fst_min_clb_speak_listen`, `language.fst_min_clb_read_write`
  - Offer/cert: `programs.requires_certificate_or_offer`
  - Funds: `proof_of_funds` unless exempt

## Integration Points

- Engine logic: `backend/src/app/rules/program_eligibility.py`
- Service facade: `backend/src/app/services/rule_engine_service.py` (`evaluate_programs`, `evaluate_full_profile`)
- Config access: `backend/src/app/domain_config/service.py`

## Traceability

- Domain knowledge references: `domain_knowledge/processed/program_families/express_entry.md`, `domain_knowledge/COVERAGE_CHECKLIST.md`
- Config sources: see `config/domain/*.yaml`
- Tests: `backend/tests/unit/rules/test_program_eligibility.py`

## Notes

- All logic is DRAFT and requires SME/legal validation before production use.
- Extend `programs.yaml` and `ProgramRule` when adding new programs or thresholds (e.g., EE PNP, study/work permits).

