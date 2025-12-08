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

## TEER & Express Entry Eligibility (Cycle 2.5 – DRAFT)

- TEER eligibility for EE core programs: TEER 0, 1, 2, 3 are “skilled” and count toward FSW/CEC/FST as applicable; TEER 4 and 5 are not eligible for EE core programs (may still be relevant for some PNP streams outside CRS).
- Engine handling:
  - For each work experience record: resolve NOC 2021 code → map to TEER → set `is_skilled_ee_eligible`.
  - Do not embed full NOC tables; rely on external lookup/config for code → TEER mapping.
  - For FSW 1-year continuous requirement, ensure same NOC/TEER 0–3; for other programs, allow multiple skilled NOCs per rules.
  - Surface when TEER 4/5 appears so eligibility gates fail unless overridden by PNP-specific logic.
- Cross-links:
  - Work experience overview for experience rules.
  - Program families (FSW/CEC/FST) for program gates.
  - CRS docs for scoring (but eligibility gate happens first).
