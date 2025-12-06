# Domain Configuration Layer (DRAFT)

Purpose: single source of truth for immigration domain rules (CRS, eligibility, points, documents). No hard-coded domain constants should live in backend/src or frontend/src; services must load domain rules through a validated ConfigService.

How to consume:

- Read via a dedicated ConfigService (backend/agent layer) that validates schema, supports versioning, and caches per environment. Do not read files ad hoc in handlers.
- Treat configs as data: tests should load sample fixtures against these schemas; production will load vetted configs.

Versioning & environments:

- Each file carries `meta.version` and `meta.status` (DRAFT). Future environments may support draft/staging/production overlays.
- Changes to domain rules must update these YAMLs, add/adjust tests, and log in ENGINEERING_LOG; user-visible impacts must update PRODUCT_LOG/BACKLOG.

Files:

- `crs.yaml` – CRS factor schema (age, education, language, work, spouse, transferability, additional points).
- `programs.yaml` – Program catalog and references to domain knowledge.
- `language.yaml` – Language test schemas and CLB mapping placeholders.
- `work_experience.yaml` – Canadian/foreign work structures, TEER/NOC linkage.
- `proof_of_funds.yaml` – Funds threshold schema and exemptions.
- `documents.yaml` – Document categories and requirement schema.

Status: DRAFT – structure only; real rule values must be ingested from `domain_knowledge/` and official IRCC sources before use.
