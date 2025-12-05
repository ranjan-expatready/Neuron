# Backend Engineering Governance Notes

- Backend contributors must follow `docs/ENGINEERING_GOVERNANCE.md` before touching `backend/src/app/**` or `backend/tests/**`.
- CI guardrails (`backend-tests`) enforce pytest with ≥80% coverage; run `make test-backend` locally first.
- All meaningful backend changes must append to `.ai-memory/ENGINEERING_LOG.md` and, if API-facing, update `PRODUCT_LOG.md`.
