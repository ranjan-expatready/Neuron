# LMIA & Job Offer – Overview (DRAFT, Engineering View)

## Purpose
Captures Labour Market Impact Assessment (LMIA) context and job offer attributes relevant to eligibility and CRS additional points.

## Key Entities / Fields
- Job offer: employer, NOC/TEER, duration, province, wage, full-time flag.
- LMIA: stream, decision, expiry, exempt category (if any).
- Arranged employment criteria (supported LMIA vs. exempt).

## Relationships
- CRS additional points depend on NOC/TEER level and validity of LMIA/exemption.
- Work permits and PNP streams may depend on LMIA or exemptions.

## Suggested Data Model (draft)
- `job_offer { id, candidate_id, employer_name, noc_code, teer_level, province, full_time_flag, duration_months }`
- `lmia_record { job_offer_id, stream, decision, issued_on, expires_on, exempt_category }`
- `crs_arranged_employment_points { teer_level, points }`

## Sources
- See `domain_knowledge/raw/lmia/sources.md`

## Status
- DRAFT – requires SME/legal review before production.

