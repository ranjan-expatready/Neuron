## 2025-12-06 – [domain][ircc_foundation][octagon] Foundational IRCC knowledge seed (DRAFT)

- Designed an IRCC domain taxonomy under `domain_knowledge/raw` and `domain_knowledge/processed` for CRS, language, work, education, NOC, LMIA, funds, docs, biometrics/medicals, and major program families (EE/PNP/Study/Work/Family/Visitor/Temp/Humanitarian).
- Collected key IRCC URLs (via Octagon-style research) into `raw/**/sources.md`, each labeled draft/not legally verified.
- Authored engineer-facing DRAFT overviews for core building blocks, program families, and lifecycle to guide data models, APIs, and workflows.
- Established `domain_knowledge/index.md` as the entry point; all content marked DRAFT pending SME/legal validation.

## 2025-12-06 – [governance][domain][octagon] Hybrid domain knowledge pipeline

- Created `domain_knowledge/` (with README) as the canonical store for immigration raw evidence and processed summaries.
- Documented the Octagon discovery/harvest/structuring workflow in `docs/OCTAGON_DOMAIN_PIPELINE.md` so research stays traceable.
- Updated `docs/ENGINEERING_GOVERNANCE.md` with a mandatory domain knowledge check before CRS/eligibility/backlog work, clarifying Octagon’s helper role.
- Extended `.ai-knowledge-base.json` with `domain_knowledge` metadata plus `external_tools.octagon` so future agents follow the pipeline.

## 2025-12-06 – [product][governance][backlog] Product log + backlog synthesized from blueprints

- [docs] Rebuilt `PRODUCT_LOG.md` so every domain (A–G) now lists ✅/🟡/🔴/🔵 capabilities mapped to `[BP-03…BP-14]` and current implementation reality.
- [backlog] Created `PRODUCT_BACKLOG.md` with 40+ items across Platform, Access, Cases, Documents, Brain, Automation, Analytics, and Expansion to capture all 🔴/🟡 blueprint gaps.
- [kb] Extended `.ai-knowledge-base.json` with a `backlog` pointer + usage rules so agents reference backlog IDs before starting work.
- [memory] Logged this governance update so future sessions treat PRODUCT_LOG + PRODUCT_BACKLOG as the canonical product state.

## 2025-12-05 – [governance][memory] Engineering governance loop in place

- [docs] Added `docs/ENGINEERING_GOVERNANCE.md` covering agent bootstrap, change types, log rules, and CI guardrails.
- [kb] Extended `.ai-knowledge-base.json` with a governance section pointing to the doc, ENGINEERING_LOG, and PRODUCT_LOG plus mandatory rules.
- [product] Noted in PRODUCT_LOG that governance is now a required part of DevOps/CI/CD so future sessions honor persistent memory.

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
