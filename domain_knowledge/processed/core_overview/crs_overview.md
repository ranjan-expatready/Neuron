# CRS – Engineering Overview (Processed) – DRAFT

> Source of truth must be the official IRCC CRS page and linked Program Delivery Instructions. No values are final until populated from those sources.

## 1. Data Model Impact

- Person (marital status, age, siblings in Canada)
- LanguageTest (type, test date/validity, CLB per skill)
- EducationCredential (level, ECA result, Canadian vs foreign, Canadian study flag/duration)
- WorkExperience (Canada, foreign; NOC/TEER, start/end, hours/week, continuity)
- Offer (NOC/TEER, LMIA flag/category, employer, duration)
- PNPNomination (province, issue date, EE-aligned flag)
- Spouse/Common-law Partner (language, education, Canadian work)
- ProgramFlags (French bonus eligibility, sibling in Canada)

## 2. Computation Engine Logic (Deterministic)

1. Determine marital status → choose tables “with spouse” vs “without spouse”.
2. Validate inputs: CLB per skill, age (exact years), education level + ECA, Canadian/foreign work, NOC/TEER for offers, nomination status.
3. Compute Core/Human Capital points:
   - Age bracket points (with/without spouse).
   - Education points (with/without spouse).
   - First official language points per skill (CLB bands; with/without spouse).
   - Canadian work experience points (with/without spouse).
   - If married, add spouse sub-factors (education, language, Canadian work).
4. Compute Skill Transferability:
   - Education × Language (CLB thresholds).
   - Education × Canadian work.
   - Foreign work × Language.
   - Foreign work × Canadian work.
   - Certificate of qualification × Language.
   - Apply category caps per IRCC table.
5. Compute Additional Points:
   - PNP nomination (600).
   - Arranged employment (LMIA-backed / eligible NOC/TEER categories).
   - Canadian study (1–2 yr; 3+ yr) if applicable.
   - French-language bonus (per CLB/IELTS/CELPIP/TEF/TCF thresholds; with/without English).
   - Sibling in Canada (meets status/residence criteria).
   - Other IRCC-listed bonuses (if present in official table).
6. Sum = CRS total. Enforce maximum caps defined by IRCC tables (e.g., transferability section caps).

## 3. Known Edge Cases / Validation

- Dual language tests: ensure correct first/second official language assignment; prevent double-counting.
- Age calculation: use exact age on assessment/ITA date; ensure boundaries at birthdays.
- Work experience gaps: continuous vs non-continuous rules for Canadian vs foreign experience.
- TEER/NOC mismatches for arranged employment: validate eligible NOC/TEER before awarding job-offer points.
- Expired tests/ECA: zero points if validity lapsed.
- Spouse missing data: spouse factors = 0 if not provided.
- PNP nomination exclusivity: only one 600-point nomination applied.
- TODO – Confirm French bonus thresholds and interaction with English CLB from official table.

## 4. TODO for Next Ingestion Cycle

- Populate all point values and CLB thresholds directly from the official CRS tables (core, spouse, transferability, additional).
- Add exact CLB↔score mappings for IELTS/CELPIP/TEF/TCF from official tables.
- Link CRS computation to eligibility programs (FSW 67-point grid, CEC, FST) in a separate eligibility module.
- Add citations (section anchors) for each factor in the processed file once fetched.
- Validate arranged-employment NOC/TEER categories against current IRCC definitions and MI updates.

## 5. Fresh Browser Ingestion (2025-12-07, DRAFT, NOT LEGAL ADVICE)

- Source: [CRS criteria](https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score/crs-criteria.html) (date modified 2025-08-21).
- Job-offer points removed (Mar 25, 2025); keep job-offer factor disabled until IRCC reintroduces.
- Core caps observed: Age (100/110), Education (140/150), Language (150/160), Canadian work (70/80).
- Spouse caps: 40 total (10 education, 20 language, 10 Canadian work).
- Transferability caps: 50 per bundle (education×language/Cdn work, foreign work×language/Cdn work, certificate×language).
- Additional points: PNP 600; French up to 50; Canadian study up to 30; sibling 15; job offer 0.

## 6. Engineering-ready data fields (update)

- `crs.core.age.bracket_points`: map age to points with/without spouse.
- `crs.core.education.points`: by credential tier.
- `crs.core.language.first.per_ability_points` and `crs.core.language.second.per_ability_points`.
- `crs.core.canadian_work.points`.
- `crs.spouse.{education,language,canadian_work}.points`.
- `crs.transferability.{education_language,education_canadian_work,foreign_work_language,foreign_work_canadian_work,certificate_language}` with per-bundle caps (50).
- `crs.additional.{pnp,canadian_study,job_offer_disabled,french_bonus,sibling}`.

## 7. Change sensitivity

- Watch IRCC “Date modified”; current 2025-08-21.
- If job-offer points reappear, re-enable and sync TEER/NOC logic; until then keep zeroed.
- Update CLB mappings and point tables on any IRCC change; drive from `config/domain/*.yaml` in future wiring.
