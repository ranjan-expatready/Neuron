# NOC / TEER – Classification Overview (DRAFT, Engineering View)

## Purpose
Provides occupational taxonomy to determine if work is “skilled” and maps to CRS/eligibility rules.

## Key Entities / Fields
- NOC code (version, e.g., NOC 2021), TEER level, title, description.
- Example duties (for self-verification), associated industry.
- Versioning (NOC 2021 vs earlier).

## Relationships
- Work experience records reference NOC/TEER.
- Eligibility programs specify minimum TEER levels (e.g., TEER 0/1/2/3).
- Job offers/LMIA also tied to NOC codes.

## Suggested Data Model (draft)
- `noc_code { code, version, teer_level, title, description }`
- `noc_example_duty { noc_code, text }`
- `noc_version_map { old_code, new_code, version_from, version_to }`

## Sources
- See `domain_knowledge/raw/noc/sources.md`

## Status
- DRAFT – requires SME/legal review before production.
