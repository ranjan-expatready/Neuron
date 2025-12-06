# Domain Knowledge Index (DRAFT – Not Legally Verified)

This index points to IRCC-related materials stored in this repository. All content is **DRAFT** and for engineering/product design only; it is **not legal advice** and requires SME/legal validation before production use.

## Raw Evidence (source URLs / notes)
- `raw/crs/` – CRS & Express Entry scoring sources.
- `raw/language/` – Language test requirements (IELTS/CELPIP/TEF/etc.).
- `raw/work_experience/` – Skilled work definitions, full-time equivalence.
- `raw/education/` – ECA requirements, Canadian vs. foreign credentials.
- `raw/noc/` – NOC/TEER classification references.
- `raw/lmia/` – LMIA basics and job offer requirements.
- `raw/proof_of_funds/` – Funds thresholds and guidance.
- `raw/documents/` – Standard document/evidence lists.
- `raw/biometrics_medicals/` – Biometrics and medical exam guidance.
- `raw/express_entry/`, `raw/pnp/`, `raw/study/`, `raw/work/`, `raw/family/`, `raw/visitor_temp/`, `raw/humanitarian_pilots/` – Program family source links.

## Processed Summaries (engineering-facing drafts)
- `processed/crs/` – CRS core structure and points overview.
- `processed/language/` – Language factors and scoring view.
- `processed/work_experience/` – TEER/skill level mapping and experience rules.
- `processed/education/` – ECA/education factors for scoring.
- `processed/noc/` – NOC taxonomy and TEER linkage.
- `processed/lmia/` – LMIA/job-offer considerations.
- `processed/proof_of_funds/` – Funds schema and thresholds (draft).
- `processed/documents/` – Document categories and evidence hints.
- `processed/biometrics_medicals/` – Biometrics/medical steps and data points.
- `processed/program_families/` – Express Entry, PNP, Study, Work, Family, Visitor/Temp, Humanitarian/Pilots overviews.
- `processed/lifecycle/` – Generic application lifecycle (tasks/states/notifications).

## How to Use (for engineering/product)
1. Start with `processed/program_families/` to understand flows and eligibility shapes.
2. Consult core building blocks in `processed/{crs,language,noc,work_experience,education,...}` for data model hints.
3. Trace back to `raw/**/sources.md` to see the underlying IRCC URLs and notes before implementing or refining rules.
4. Treat everything here as **draft** until reviewed by an immigration SME; flag gaps in processed files before coding.
