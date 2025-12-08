# Work Experience – Structure (DRAFT, Engineering View)

## Purpose

Defines skilled work experience for eligibility and scoring (CRS, program minimums).

## Key Entities / Fields

- NOC/TEER code, occupation title.
- Duration (months), full-time equivalent hours, continuity (e.g., 1-year continuous FSW).
- Location (Canada vs. foreign), work type (paid), time window.
- Employer/job offer linkage (for LMIA/arranged employment).

## Relationships

- Tied to NOC/TEER classification; feeds CRS core and transferability factors.
- Eligibility programs (CEC/FSW/FST) apply different thresholds/TEER levels.
- LMIA/job offer may add CRS points but is distinct from experience.

## Suggested Data Model (draft)

- `work_experience { id, candidate_id, noc_code, teer_level, start_date, end_date, hours_per_week, location, paid_flag, continuous_flag }`
- `work_summary { candidate_id, canada_years, foreign_years, continuous_1yr_flag }`
- `program_rule_link { program, teer_min, min_months, recency_window }`

## Sources

- See `domain_knowledge/raw/work_experience/sources.md`

## Status

- DRAFT – requires SME/legal review before production.

### Arranged Employment (Cycle 2.5 – DRAFT)

- Concept: Qualifying job offer that meets IRCC criteria; separate from historical work experience.
- Key conditions (program-facing):
  - TEER 0/1/2/3 occupation.
  - Full-time, paid, non-seasonal; duration at least 1 year after PR issuance.
  - Usually LMIA-backed; LMIA-exempt employer-specific permits may qualify if meeting “valid job offer” rules.
  - Up to two employers can combine for some cases; employer(s) must be eligible and compliant.
- Engine considerations:
  - Model as structured job-offer entity or flag on work record: `employer_id`, `noc_code`, `teer_level`, `has_lmia`, `lmia_exemption_code`, `job_duration`, `hours_per_week`, `location`, `non_seasonal_flag`.
  - Eligibility engines should gate arranged employment separately from CRS scoring; CRS points logic stays in CRS docs.
  - FST may rely on job offer or certificate of qualification; CEC/FSW may treat job offer as optional but must meet validity rules if used.
- Cross-links:
  - CRS docs for arranged-employment points (do not repeat points here).
  - NOC/TEER overview for skilled vs non-skilled classification.
  - Program rules (FSW/CEC/FST) for how offers interplay with eligibility vs optional strength.
