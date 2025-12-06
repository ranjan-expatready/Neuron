# Application Lifecycle – Generic Flow (DRAFT)

## Overview
High-level lifecycle for immigration cases; to be specialized per program family.

## Stages (example)
1. Inquiry / Lead
2. Pre-screen / Intake
3. Eligibility assessment (program + CRS context where applicable)
4. Documentation gathering (checklists, proofs, forms)
5. Submission (e-APR or paper where relevant)
6. Biometrics / Medicals
7. ADRs / Additional evidence
8. Decision (approval/refusal)
9. Post-decision (landing, COPR/visa issuance, extensions/appeals as applicable)

## Engineering Mappings
- Case states map to stages; transitions trigger tasks/notifications.
- Checklists are stage-scoped; documents and validity windows linked to requirements.
- SLAs/alerts for biometrics/medicals/ADRs deadlines.

## Implementation Hints
- Represent lifecycle as configurable state machine per program family; reuse common states but allow overrides.
- Tie tasks to stages and program rules (e.g., biometrics required after submission; proof of funds verified before submission).

## Sources
- Draws on multiple IRCC program docs; see `domain_knowledge/raw/documents/sources.md` and program family sources.

## Status
- DRAFT – requires SME/legal review before production.
