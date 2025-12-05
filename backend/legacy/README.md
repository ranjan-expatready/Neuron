# Legacy Backend Code

This directory preserves the previous FastAPI backend implementation (`backend/app`) and its original tests (`backend/tests/test_models_simple.py`, `backend/tests/test_services.py`).

- **Canonical backend:** `backend/src/app` (used by uvicorn, Makefile, CI, and new tests)
- **Current tests:** `backend/tests/unit`, `backend/tests/integration`, `backend/tests/e2e`
- **Purpose of legacy code:** Historical reference only. Nothing in CI, docker-compose, or runtime imports code from `backend/legacy`.

When the team confirms no remaining dependencies on the legacy modules, this folder can be removed.
