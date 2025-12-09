# CRS – Core Structure (DRAFT, Engineering View)

## Purpose
Ranks Express Entry candidates using human-capital, spouse, skill-transferability, and additional factors to invite the highest-scoring profiles.

## Key Entities / Fields
- Candidate profile: age, marital status, education, first/second official language scores (CLB), work experience (Canada/foreign, TEER), job offer/LMIA, provincial nomination, Canadian study, relatives, arranged employment, French ability, siblings.
- Points tables: core factors, spouse factors, transferability combos, additional points.
- Validity: language/ECA validity windows; profile expiration.

## Relationships
- CRS draws on NOC/TEER (for work skill level), language (CLB), education (ECA/Canadian), LMIA/job offers, and provincial nominations (PNP).
- Program eligibility (FSW/CEC/FST) gates entry; CRS ranks after eligibility.

## Suggested Data Model (draft)
- `crs_factor { id, name, category, max_points }`
- `crs_subfactor { factor_id, name, criteria_ref, max_points }`
- `crs_points_table { subfactor_id, condition_expr, points }` (condition references CLB, age ranges, TEER years, education level, etc.)
- `eligibility_program_link { program, crs_applicability }`

## Sources
- See `domain_knowledge/raw/crs/sources.md`

## Status
- DRAFT – requires SME/legal review before production.

