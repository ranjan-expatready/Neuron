# CRS Skill Transferability & Additional Points (ENGINEERING DRAFT — NOT LEGAL ADVICE)

## What transferability is
- CRS awards up to 100 points for combinations of education, language (CLB/NCLC), Canadian work, foreign work, and certificates of qualification.
- Transferability layers on top of core human capital and spouse factors; caps apply per bundle (usually 50) and 100 total.
- Additional points (PNP, French, sibling, Canadian study, etc.) stack after transferability.

## How to model
- Read tables from `domain_knowledge/raw/crs/transferability_tables.md`; do not hard-code constants.
- Represent each bundle as a structured lookup (education × language, education × Canadian work, foreign work × language, foreign work × Canadian work, certificate × language).
- Respect caps: each sub-bundle max 50; total transferability max 100.
- Additional points: apply after transferability (PNP 600, French up to 50, sibling 15, Canadian study 15/30).
- Job-offer points: not present on the current IRCC CRS criteria page (removed per Mar 25, 2025 notice).

## Implementation hints
- Condition evaluation should use CLB/NCLC derived from language tables (see `raw/language/clb_tables.md`).
- Apply program eligibility gates first (FSW/CEC/FST) before CRS ranking.
- Keep version/date metadata from source page (Date modified: 2025-08-21).
- Store raw values in config (future `config/domain/crs.yaml`) and validate against benchmarks; allow SME-reviewed overrides.

## Sources
- `domain_knowledge/raw/crs/transferability_sources.md`
- `domain_knowledge/raw/crs/transferability_tables.md`
- Related: `domain_knowledge/raw/crs/sources.md`, `domain_knowledge/processed/crs/core_overview.md`

Status: DRAFT — SME/legal validation required before production use.

