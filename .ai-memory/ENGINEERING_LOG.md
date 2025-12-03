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
