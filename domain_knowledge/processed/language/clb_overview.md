# CLB/NCLC Equivalency Overview (ENGINEERING DRAFT — NOT LEGAL ADVICE)

## Scope
- Tests covered (IRCC accepted): CELPIP General, IELTS General Training, PTE Core, TEF Canada, TCF Canada.
- Source for equivalency tables: IRCC “How to find your language level based on your test results” (PGWP) page (Date modified: 2025-07-09).
- Source for program minima: IRCC “Express Entry: Language test results” (Date modified: 2025-08-21).

## How CLB/NCLC mapping works
- Each approved test reports scores per ability (Reading, Writing, Listening, Speaking).
- IRCC publishes score → CLB/NCLC tables per test; use these tables to convert raw scores to benchmark levels.
- CLB/NCLC are then used to evaluate program-specific minimums (FSW, CEC, FST) and to drive CRS language factors (via CLB).

## Program minimums (from Express Entry: Language test results)
- CEC: TEER 0/1 → CLB/NCLC 7; TEER 2/3 → CLB/NCLC 5.
- FSW: First official language CLB/NCLC 7; second official language CLB/NCLC 5.
- FST: Speaking/Listening CLB/NCLC 5; Reading/Writing CLB/NCLC 4.
- Tests accepted: CELPIP General, IELTS General Training, PTE Core, TEF Canada, TCF Canada.

## Where to pull exact values
- Raw tables: `domain_knowledge/raw/language/clb_tables.md`
- Source references: `domain_knowledge/raw/language/clb_sources.md`
- Program minima details: Express Entry “Language test results” page (see clb_sources.md).

## Engineering usage hints
- Store CLB/NCLC lookup tables per test/skill; support ranges where IRCC provides them (e.g., PTE ranges, TEF/TCF scaled ranges).
- Validation: ensure test result date aligns with the correct TEF table (post-2023 vs. 2019–2023).
- Keep CLB/NCLC values in config, not hard-coded; wire to CRS calculators and eligibility gates later.

Status: DRAFT — values are copied from IRCC pages but must be SME/legal validated before production use.
