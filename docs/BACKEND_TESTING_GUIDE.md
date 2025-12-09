# Backend Testing Guide

This guide explains how to extend the FastAPI backend's gold-class pytest spine.

## Test Layers

- **Unit tests (`backend/tests/unit`)**
  - Exercise pure functions, services, and schema helpers.
  - Must not rely on external services; the shared TestClient fixture is allowed for lightweight endpoint checks such as `/health`.
- **Integration tests (`backend/tests/integration`)**
  - Hit real FastAPI routes via `TestClient`, use the in-memory SQLite DB, and validate serialization + auth logic.
  - Prefer realistic end-to-end flows (e.g., register → login → domain API).

## Fixtures & `conftest.py`

`backend/tests/conftest.py` hosts the canonical testing spine:

- Spins up an in-memory SQLite database per test function and keeps production data untouched.
- Overrides `get_db` so every request within `TestClient` uses the safe session.
- Provides reusable helpers for creating users, orgs, auth headers, etc.

When adding fixtures, keep them composable and fast; reuse existing ones whenever possible.

## Adding Tests for New Features

1. Decide the right layer: pure logic → unit, API/database flows → integration (often both).
2. Import the shared fixtures from `conftest.py` (no custom clients unless strictly necessary).
3. Name files `test_<feature>.py` and decorate tests with `@pytest.mark.unit` or `@pytest.mark.integration`.
4. Run locally:
   - `cd backend && pytest`
   - `cd backend && pytest -m "unit"`
   - `cd backend && pytest -m "integration"`
5. Ensure coverage stays ≥80% and document any deliberate exclusions in PR notes.

Future agents and engineers should treat this guide as the authoritative runbook for backend test contributions.
