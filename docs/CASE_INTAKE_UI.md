# Express Entry Case Intake UI (Read-Only) – Milestone 3.3

> Frontend-only page that calls the Case Evaluation API to show program eligibility, CRS breakdown, and required forms/documents. No persistence, no payments, no edits. Not legal advice.

## Route
- `/express-entry/intake`

## How it works
1. User fills a minimal intake form (age, family size, marital status, education, language CLB scores, work experience, proof of funds, job offer flag).
2. UI POSTs to `POST /api/v1/cases/evaluate` with a `CandidateProfile`-shaped payload.
3. Results panel renders:
   - Program eligibility (FSW/CEC/FST) with reasons.
   - CRS breakdown total + factor groups.
   - Required forms and documents from DocumentMatrix/CaseService output.

## Current limitations
- Read-only; single-session (no DB persistence, no save/export).
- Auth behavior depends on backend; if API is unreachable, a banner is shown and no mock results are injected (layout-only).
- Config-first: UI does **not** hard-code IRCC thresholds; it renders whatever the API returns.

## Dev notes
- Page lives at `frontend/src/app/express-entry/intake/page.tsx`.
- Uses fetch against `/api/v1/cases/evaluate`; ensure backend is running and accessible in dev.
- Tests: `frontend/tests/case-intake.test.tsx` (Jest + Testing Library).


