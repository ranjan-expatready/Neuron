# Education – Structure (DRAFT, Engineering View)

## Purpose
Represents educational credentials for eligibility and CRS points, distinguishing Canadian credentials from foreign credentials assessed via ECA.

## Key Entities / Fields
- Credential type (high school, diploma, bachelor, master, PhD).
- Country, institution, completion date.
- ECA: designated org, report date, equivalency result, validity.
- Canadian study indicators (credential in Canada, length).

## Relationships
- Feeds CRS core and transferability (education + language).
- Eligibility (FSW requires secondary or higher; specific streams may vary).
- ECA validity windows must be tracked; language + education combos impact CRS.

## Suggested Data Model (draft)
- `education_credential { id, candidate_id, level, country, institution, completed_on, canadian_flag }`
- `eca_assessment { credential_id, org, report_date, equivalency_level, valid_until }`
- `crs_education_points { level, canadian_flag, points_primary, points_spouse }`

## Sources
- See `domain_knowledge/raw/education/sources.md`

## Status
- DRAFT – requires SME/legal review before production.
