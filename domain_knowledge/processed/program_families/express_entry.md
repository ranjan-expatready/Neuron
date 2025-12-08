# Express Entry – Program Family (DRAFT)

## Overview

Economic immigration platform for FSW, CEC, FST, and EE-aligned PNP streams. Eligibility per program; ranking via CRS.

## Sub-programs

- Federal Skilled Worker (FSW)
- Canadian Experience Class (CEC)
- Federal Skilled Trades (FST)
- Express Entry PNP (EE-aligned)

## Eligibility Structure (high-level)

- Program gates: language (CLB thresholds), work experience (TEER/skill level), education/ECA (FSW), proof of funds (if applicable), admissibility.
- FSW also has a separate 67-point eligibility grid before CRS ranking.
- CRS ranking applies after eligibility; draws issue ITAs.

## Key Decision Dimensions

- Age, language (CLB), education/ECA, Canadian/foreign work, NOC/TEER, arranged employment/LMIA, provincial nomination, proof of funds, relatives in Canada.

## Typical Journeys

- Candidate creates EE profile → obtains language/ECA → enters pool → receives ITA → submits e-APR with documents → biometrics/medicals → decision.

## Implementation Hints

- Config-driven program definitions (FSW/CEC/FST) with reusable building blocks (language, work, education, funds).
- CRS engine consumes standardized profile attributes; program eligibility uses the same core entities with program-specific thresholds.

### Program Rules (Cycle 2.4 – DRAFT, SME VALIDATION REQUIRED)

- Federal Skilled Worker (FSW)
  - Work: ≥1 year continuous full-time (or equivalent part-time) skilled work in same NOC/TEER category (historic NOC 0/A/B → TEER 0–3) within last 10 years.
  - Language: CLB 7 in each skill (reuse CLB tables already ingested).
  - Education: secondary or above; foreign education requires ECA equivalency.
  - Funds: proof of funds unless exempt (valid job offer + authorization).
  - FSW 67-point grid applies before CRS; factors (language, education, work, age, arranged employment, adaptability) should be modeled structurally, not hard-coded here.
- Canadian Experience Class (CEC)
  - Work: ≥1 year authorized skilled Canadian work in last 3 years; part-time can combine to full-time equivalence; self-employment generally excluded.
  - Language: TEER 0/1 → CLB 7; TEER 2/3 → CLB 5 (reuse CLB tables).
  - Funds: typically not required for CEC.
- Federal Skilled Trades (FST)
  - Work: ≥2 years full-time (or equivalent) skilled trades work in last 5 years.
  - Job offer/certification: valid job offer (≥1 year) OR certificate of qualification from Canadian authority.
  - Language: minimum CLB 5 speaking/listening and CLB 4 reading/writing.
  - Funds: generally required unless exempt via job offer/work authorization.
- PNP (Express Entry–aligned)
  - Enhanced streams issue nomination → +600 CRS points (see CRS docs); candidate must still meet EE program eligibility and hold an EE profile.
  - Non-EE PNP streams run outside CRS; do not mix into EE scoring.
- Engineering notes
  - Evaluate program gate before CRS; block CRS scoring if gate fails.
  - Map work to TEER/NOC and handle continuous vs equivalent part-time logic explicitly.
  - Reuse existing CLB tables, proof-of-funds rules, and work/education models; avoid duplicate numeric values here.
  - Mark all values DRAFT; SME/legal validation required before production.

## Sources

- See `domain_knowledge/raw/express_entry/sources.md` and related core raw folders.

## Status

- DRAFT – requires SME/legal review before production.
