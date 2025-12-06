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

## Sources
- See `domain_knowledge/raw/express_entry/sources.md` and related core raw folders.

## Status
- DRAFT – requires SME/legal review before production.
