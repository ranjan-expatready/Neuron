## 2025-12-06 – [domain][crs][octagon_ingest_v1] CRS ingestion attempt (DRAFT)

- Targeted CRS domain ingestion using official IRCC/Canada.ca URLs (CRS page, eligibility page, NOC site). Network access unavailable in this environment; raw file documents sources + TODOs to populate exact tables.
- Added `domain_knowledge/raw/crs/sources.md` with official URLs and explicit TODO to copy full CRS point tables (core/spouse/transferability/additional) once accessible.
- Added processed overview `domain_knowledge/processed/core_overview/crs_overview.md` outlining data model and deterministic CRS computation steps, with TODOs to inject exact point values/CLB thresholds when fetched.
- No code or workflow changes; content remains DRAFT until IRCC tables are imported verbatim.

## 2025-12-06 – [config][domain][governance] Config-first domain layer established (DRAFT)

- Created `config/domain/` with draft schemas (`crs.yaml`, `programs.yaml`, `language.yaml`, `work_experience.yaml`, `proof_of_funds.yaml`, `documents.yaml`) plus README stating config-first rules; no real IRCC values added.
- Updated `docs/ENGINEERING_GOVERNANCE.md` with Config-First Domain Rules: no hard-coded thresholds; all changes must flow through config/domain + tests + logs/product updates.
- Extended `.ai-knowledge-base.json` with `config_domain` pointers; added PRODUCT_LOG bullet and PRODUCT_BACKLOG items `[CFG-001..003]` for ConfigService, CI guard, and admin UI.
- No runtime wiring yet; tests unchanged (not run in this docs/config task).

## 2025-12-06 – [product][governance][backlog] Product log + backlog synthesized from blueprints

- [docs] Rebuilt `PRODUCT_LOG.md` so every domain (A–G) now lists ✅/🟡/🔴/🔵 capabilities mapped to `[BP-03…BP-14]` and current implementation reality.
- [backlog] Created `PRODUCT_BACKLOG.md` with 40+ items across Platform, Access, Cases, Documents, Brain, Automation, Analytics, and Expansion to capture all 🔴/🟡 blueprint gaps.
- [kb] Extended `.ai-knowledge-base.json` with a `backlog` pointer + usage rules so agents reference backlog IDs before starting work.
- [memory] Logged this governance update so future sessions treat PRODUCT_LOG + PRODUCT_BACKLOG as the canonical product state.

## 2025-12-06 – [product][governance][backlog] Product log + backlog synthesized from blueprints

- [docs] Rebuilt `PRODUCT_LOG.md` so every domain (A–G) now lists ✅/🟡/🔴/🔵 capabilities mapped to `[BP-03…BP-14]` and current implementation reality.
- [backlog] Created `PRODUCT_BACKLOG.md` with 40+ items across Platform, Access, Cases, Documents, Brain, Automation, Analytics, and Expansion to capture all 🔴/🟡 blueprint gaps.
- [kb] Extended `.ai-knowledge-base.json` with a `backlog` pointer + usage rules so agents reference backlog IDs before starting work.
- [memory] Logged this governance update so future sessions treat PRODUCT_LOG + PRODUCT_BACKLOG as the canonical product state.

## 2025-12-05 – [governance][memory] Engineering governance loop in place

- [docs] Added `docs/ENGINEERING_GOVERNANCE.md` covering agent bootstrap, change types, log rules, and CI guardrails.
- [kb] Extended `.ai-knowledge-base.json` with a governance section pointing to the doc, ENGINEERING_LOG, and PRODUCT_LOG plus mandatory rules.
- [product] Noted in PRODUCT_LOG that governance is now a required part of DevOps/CI/CD so future sessions honor persistent memory.

## 2025-12-05 – CI guardrails live on main

- [branch-protection] Switched `main` protection to require the GitHub Actions jobs `backend-tests` and `frontend-tests` (strict up-to-date, app_id=15368), kept force-push/delete disabled, and relaxed review count to 0 for solo maintainer flow.
- [ci] Gave backend/frontend workflows unique job names, regenerated runs, and confirmed both pipelines pass after the `.env` + Codecov fixes.
- [merge] With required checks green, merged PR #2 `chore(ci): standardize CI and guardrails` into `main` (auto-deleted `ci-guardrails-setup`).
- [next] Documented the guardrails activation in PRODUCT_LOG and knowledge base so future agents treat backend/frontend CI as required gates for every PR.

## 2025-12-05 – CI guardrails live on main

- [branch-protection] Updated `main` protection to require the GitHub Actions jobs `backend-tests` and `frontend-tests` (strict up-to-date, app_id=15368) while keeping force-push/delete disabled and relaxing approving reviews to 0 for solo maintenance.
- [ci] Renamed backend/frontend workflow jobs so each status has a unique context, regenerated runs after the `.env`/Codecov fixes, and confirmed both pipelines are green.
- [merge] Merged PR #2 `chore(ci): standardize CI and guardrails` into `main` and auto-deleted `ci-guardrails-setup`.
- [docs] Refreshed PRODUCT_LOG + knowledge base so future agents treat backend/frontend CI as required gates on every PR.

## 2025-12-03 – Stabilization & E2E Spine

- [backend] Standardized runtime on Python 3.10.19 with `backend/.venv`, fixed `psycopg2`/`pydantic-settings` compatibility, and added `make e2e-*` helpers plus shared `/api/v1/auth/login` ↔ `/login-json` helper in `backend/src/app/api/routes/auth.py`.
- [cases/documents] Reworked Case/Person services to align fixtures, added `/cases/new` flow, ensured document uploads set `category`, and hardened `/api/v1/documents/*` + `/api/v1/cases/*` integrations.
- [frontend] Implemented auth context JSON login, `/cases/new` UI with stable `data-testid`s, dashboard new-case button, case detail/document upload wiring.
- [tests] Restored backend pytest spine (auth/cases/documents green), fixed Playwright markers, and refreshed TestSprite API suites (TC002/TC003).
- [e2e] Built canonical TC000_Full_User_Journey (login → dashboard → case creation → upload) plus `docs/E2E_SPINE_SETUP.md` and `.ai-knowledge-base` entries pointing to `sqlite:///./e2e.db`.

## 2025-12-03 – Backend src promotion & coverage

- [backend] Adopted `backend/src/app` as the canonical FastAPI implementation, wired uvicorn/docker/make targets, and moved the legacy `backend/app` tree plus early pytest files into `backend/legacy/` with a README.
- [tests] Checked in the restored pytest spine under `backend/tests/{unit,integration,e2e}`, aligned fixtures with `src.app` imports, and kept Playwright e2e gated by `RUN_E2E`.
- [ci] Updated `backend-ci` to install Playwright browsers and leveraged the existing pytest.ini coverage gate (≥80%); local run now reports ~82.2% line coverage across `src/app`.
- [lint] Ran ruff/black on the new source, normalized exception handling (`raise … from err`), and configured ruff to keep Optional[...] syntax until a broader typing pass.

## 2025-12-07 – [domain][ircc_ingest_browser][coverage_v1]

- Created `domain_knowledge/COVERAGE_CHECKLIST.md` summarizing Cycle 1 coverage for CRS, language, work_experience, education, NOC, proof_of_funds, documents, biometrics_medicals, and Express Entry.
- Added backlog items [IRCC-201..205] for CLB mappings, CRS transferability, language thresholds, NOC crosswalk, and biometrics/medical rules.
- Documentation-only change; no runtime code or configs modified.

## 2025-12-07 – [domain][language][clb_cycle_2_1]
- Ingested CLB/NCLC tables (CELPIP-G, IELTS GT, PTE Core, TEF Canada post-2023 and 2019–2023, TCF Canada) from IRCC PGWP language-results page (2025-07-09).
- Recorded program minima from Express Entry language-test page (2025-08-21) for CEC TEER splits, FSW first/second, and FST thresholds.
- Files: `domain_knowledge/raw/language/clb_sources.md`, `clb_tables.md`, `processed/language/clb_overview.md`; references added in processed overview.
- Status: DRAFT; SME/legal validation still required; no backend/frontend/config changes.

## 2025-12-08 – [domain][ircc_cycle2][crs_transferability_ingest_v1]
- Ingested CRS skill transferability and additional-points tables from IRCC CRS criteria page (check-score/crs-criteria.html, date modified 2025-08-21) via HTTP fetch (Browser Tab unavailable in session).
- Added raw sources/tables: `domain_knowledge/raw/crs/transferability_sources.md`, `domain_knowledge/raw/crs/transferability_tables.md` (education+language, education+Canadian work, foreign work+language, foreign work+Canadian work, certificate+language; additional points PNP/French/sibling/Canadian study).
- Added processed overview: `domain_knowledge/processed/core_overview/crs_transferability.md` with engineering guidance to read tables from config (DRAFT, SME validation pending).
- Updated coverage checklist to reflect transferability tables captured (still DRAFT) and set IRCC-202 to In Progress.
- No backend/frontend/config runtime changes; documentation/domain knowledge only.

## 2025-12-08 – [governance][repo_hygiene][docs_only]
- Added repo hygiene & branch workflow rules to `docs/ENGINEERING_GOVERNANCE.md` (feature branches, clean main, protection template, automation expectations).
- Extended `.ai-knowledge-base.json` with `repo_hygiene` rules pointer.
- Backlog: added [ENG-999] Repo hygiene monitor (planned) to enforce clean main/branch protection.
- Docs-only; no runtime code or configs changed.

## 2025-12-08 – [domain][ircc_cycle2][biometrics_medicals_validity_v1]
- Ingested biometrics/medical validity & reuse from IRCC (biometrics page; temp/PR medical exam pages); captured in `raw/biometrics_medicals/validity_sources.md` + `validity_tables.md` and updated processed overview.
- Updated coverage checklist (Biometrics/Medicals) and backlog IRCC-205 to reflect Cycle 2.3 progress (validity/reuse drafted; implementation pending).
- Domain-only documentation; no runtime code changes.
