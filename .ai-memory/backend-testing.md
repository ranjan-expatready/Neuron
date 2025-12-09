# Backend Testing Spine

- Tests live in `backend/tests/{unit,integration}` with shared fixtures in `backend/tests/conftest.py`.
- Run commands: `cd backend && pytest`, or filter via `pytest -m "unit"` / `pytest -m "integration"`.
- See `docs/BACKEND_TESTING_GUIDE.md` for layering and fixture instructions.
