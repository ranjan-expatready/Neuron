# IRCC Domain Coverage Checklist (Cycle 1 – Browser Ingest)

> Status key:
>
> - ✅ = reasonably covered for engineering design (not legal)
> - 🟡 = partially covered / missing important pieces
> - 🔴 = largely missing
>
> Sources for this checklist:
>
> - `domain_knowledge/raw/**`
> - `domain_knowledge/processed/**`
> - `.ai-memory/ENGINEERING_LOG.md` entries tagged `[domain][ircc_ingest_browser]`

## 1. Core Building Blocks

### 1.1 CRS (Comprehensive Ranking System)

- Status: 🟡
- Raw: `domain_knowledge/raw/crs/sources.md`
- Processed: `domain_knowledge/processed/core_overview/crs_overview.md`
- Covered: core/spouse maxima; age/education/language/Canadian work tables; additional points; job-offer points removal note (2025-03-25); transferability caps at 50 bundles.
- Missing / TODO (Cycle 2): CLB-to-test mappings; full skill-transferability breakdowns per combination; citations/anchors per table; confirm French bonus thresholds; eligibility grid linkage.

### 1.2 Language

- Status: 🟡
- Raw: `domain_knowledge/raw/language/sources.md`
- Processed: `domain_knowledge/processed/language/overview.md`
- Covered: accepted tests (CELPIP-G, IELTS GT, PTE Core, TEF, TCF); program minima (CEC TEER split, FSW first/second, FST split); validity <2 years.
- Missing / TODO: Detailed CLB ↔ score tables per test/skill; second-language CRS points table; expiry edge cases; IELTS One Skill Retake policy monitoring.

### 1.3 Work Experience

- Status: 🟡
- Raw: `domain_knowledge/raw/work_experience/sources.md`
- Processed: `domain_knowledge/processed/work_experience/overview.md`
- Covered: Program gates (CEC TEER CLB splits, FSW continuous year, FST trades); TEER summary; Canadian vs foreign separation.
- Missing / TODO: Continuous vs cumulative rules per program; recency rules; hour/week normalization; cross-links to NOC eligibility for arranged employment.

### 1.4 Education / ECA

- Status: 🟡
- Raw: `domain_knowledge/raw/education/sources.md`
- Processed: `domain_knowledge/processed/education/overview.md`
- Covered: ECA required for foreign credentials; approved issuer requirement; validity considerations.
- Missing / TODO: Approved ECA issuer list; expiry windows; mapping to CRS education points with citations; Canadian study bonus linkage.

### 1.5 NOC / TEER

- Status: 🟡
- Raw: `domain_knowledge/raw/noc/sources.md`
- Processed: `domain_knowledge/processed/noc/overview.md`
- Covered: NOC 2021 adoption; TEER 0–5 definitions and examples; link to official NOC search.
- Missing / TODO: Full NOC code crosswalk; mapping guidance for arranged employment eligibility; change-monitor strategy for NOC updates.

### 1.6 Proof of Funds

- Status: ✅
- Raw: `domain_knowledge/raw/proof_of_funds/sources.md`
- Processed: `domain_knowledge/processed/proof_of_funds/overview.md`
- Covered: 2025-07-07 CAD table; exemptions (CEC, valid job offer + work auth); acceptable evidence; accessibility/borrowing rules.
- Missing / TODO: FX conversion rules; automation hooks for annual updates; evidence validation examples.

### 1.7 Documents

- Status: 🟡 (Cycle 2.4 – ADR patterns captured; SME validation pending)
- Raw: `domain_knowledge/raw/documents/sources.md`, `domain_knowledge/raw/documents/adr_sources.md`
- Processed: `domain_knowledge/processed/documents/overview.md`, `domain_knowledge/processed/documents/adr_overview.md`
- Covered: EE profile vs e-APR doc expectations (language test, ECA, PoF, police, medical, job offer, PNP); ADR patterns (work, funds, education, identity/police, medical/biometrics), workflows (deadlines, portal upload), engineering flags.
- Missing / TODO: Per-program checklist granularity; detailed ADR-to-checklist rules; validity windows (police/medical); automation and SME validation.

### 1.8 Biometrics & Medicals

- Status: 🟡 (Cycle 2.3 – validity/reuse ingested; SME validation pending)
- Raw: `domain_knowledge/raw/biometrics_medicals/sources.md`, `domain_knowledge/raw/biometrics_medicals/validity_sources.md`, `domain_knowledge/raw/biometrics_medicals/validity_tables.md`
- Processed: `domain_knowledge/processed/biometrics_medicals/overview.md`
- Covered: Biometrics age scope (14–79), reuse allowed when prior biometrics still valid (per IRCC status tool); medical exam validity 12 months (temp + PR), panel physician requirement, need new IME after expiry; deadlines/fee timing retained.
- Missing / TODO: Program-specific biometrics/fee waivers, ADR patterns, automation of validity checks and reminders; SME/legal validation of validity tables.

### 1.9 Express Entry Program Family

- Status: 🟡 (Cycle 2.4 program rules captured; SME validation pending)
- Raw: `domain_knowledge/raw/express_entry/sources.md`, `domain_knowledge/raw/express_entry/program_rules_sources.md`
- Processed: `domain_knowledge/processed/program_families/express_entry.md`
- Covered: FSW/CEC/FST program rules (language, work, education/ECA, funds), +600 PNP nomination, program gate before CRS, continuous vs part-time equivalence, reuse of CLB/PoF/work models.
- Missing / TODO: Full FSW 67-point grid, detailed trades list, province-specific PNP rules, draw/category-based selection references, SME validation and engine wiring.

## 2. Summary for Engineering Planning

- Strong (ok for initial design): Proof of funds.
- Medium (needs another ingestion pass before implementation): CRS, Language, Work experience, Education/ECA, NOC/TEER, Documents, Biometrics/Medicals, Express Entry family.
- Weak: none in scope, but CRS/Language need precise tables before production calculators.

## 3. Recommended Next IRCC Ingestion Cycle

- Focus 1: CLB-to-test score mappings + full CRS transferability tables with citations.
- Focus 2: Medical/biometrics validity, reuse rules, and checklist automation.
- Focus 3: NOC/TEER crosswalk details and arranged-employment eligibility mapping.
