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
