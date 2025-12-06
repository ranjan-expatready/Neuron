# Language – Scoring & Requirements (DRAFT, Engineering View)

## Purpose
Captures official language proficiency for eligibility and CRS points (first and second official language).

## Key Entities / Fields
- Test type (IELTS-G, CELPIP-G, TEF Canada, TCF Canada), test date, validity.
- CLB level per skill: reading, writing, listening, speaking.
- Program thresholds (FSW/CEC/FST) and CRS point mappings (primary vs. secondary language).

## Relationships
- Feeds CRS core and additional points; eligibility gates per program (e.g., CLB 7/5).
- Interacts with skill transferability (education + language, foreign work + language).

## Suggested Data Model (draft)
- `language_test { id, candidate_id, test_type, test_date, expires_at }`
- `language_scores { test_id, skill, clb_level, raw_score }`
- `program_threshold { program, skill, min_clb }`
- `crs_language_points { clb_range, points_primary, points_secondary }`

## Sources
- See `domain_knowledge/raw/language/sources.md`

## Status
- DRAFT – requires SME/legal review before production.
