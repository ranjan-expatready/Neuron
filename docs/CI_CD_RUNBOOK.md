# CI/CD Runbook

This project enforces a FAANG-grade CI/CD pipeline with dedicated workflows for backend tests, frontend lint/build, and the canonical end-to-end spine. All workflows live under `.github/workflows`.

## Workflow Matrix

| Workflow           | File                                | Trigger                             | What it does                                                                                        |
| ------------------ | ----------------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------- |
| Backend CI         | `.github/workflows/backend-ci.yml`  | `pull_request` -> `main`, `develop` | Sets up Python 3.10, installs backend deps, runs `pytest --cov=src --cov-fail-under=80`             |
| Frontend CI        | `.github/workflows/frontend-ci.yml` | `pull_request` -> `main`, `develop` | Installs npm deps, runs `npm run lint` and `npm run build`                                          |
| E2E Spine (manual) | `.github/workflows/e2e-spine.yml`   | `workflow_dispatch` (manual)        | Seeds `sqlite:///./e2e.db` via `make e2e-db-reset`; documents prerequisites for running TC000 in CI |

## Makefile > CI mapping

| Make target          | Location                       | Mirrors workflow                                                                              |
| -------------------- | ------------------------------ | --------------------------------------------------------------------------------------------- |
| `make test-backend`  | `backend/Makefile`             | Same steps as Backend CI (`pytest --cov=src --cov-fail-under=80`)                             |
| `make test-frontend` | (root or frontend make target) | Runs `npm run lint && npm run build` just like Frontend CI                                    |
| `make e2e-spine`     | `backend/Makefile`             | Local/manual equivalent of the E2E spine workflow (requires backend/frontend servers running) |

## Required Checks for `main`

- `backend-ci`
- `frontend-ci`

`e2e-spine` is currently manual/optional until the GitHub workflow includes full headless TC000 execution.

## Running CI locally

1. **Backend**:
   ```bash
   cd backend
   source .venv/bin/activate
   make test-backend  # pytest --cov=src --cov-fail-under=80
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm ci
   npm run lint
   npm run build
   ```
3. **E2E spine** (manual):
   ```bash
   cd backend
   source .venv/bin/activate
   make e2e-db-reset
   # In separate terminals: run backend (DATABASE_URL=sqlite:///./e2e.db uvicorn …) and frontend (npm run dev)
   make e2e-spine
   ```
