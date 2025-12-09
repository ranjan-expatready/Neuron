# Canonical E2E Spine Setup

The TC000 “Full User Journey” Playwright script exercises the golden path:

1. Login via `/auth/login` → `/dashboard`
2. Click **New Case** → `/cases/new`
3. Create a client + case → `/cases/{id}`
4. Open the Documents tab → go to `/cases/{id}/upload`
5. Upload a document → land back on `/cases/{id}` and verify it appears

Follow these terminals to run the journey locally.

---

### Terminal 1 – Backend API (sqlite spine DB)

```bash
cd backend
source .venv/bin/activate
make e2e-db-reset
DATABASE_URL=sqlite:///./e2e.db uvicorn src.app.main:app --reload
```

`make e2e-db-reset` removes `e2e.db`, recreates the schema, and seeds the TestSprite automation user/org. Keep uvicorn running with the same `DATABASE_URL`.

### Terminal 2 – Frontend (Next.js dev server)

```bash
cd frontend
npm run dev
```

The canonical test expects the app on `http://localhost:3000`. If you change the port, export `TESTSPRITE_UI_BASE_URL` before running the spine test.

### Terminal 3 – Canonical Playwright spine

```bash
cd backend
source .venv/bin/activate
make e2e-spine
```

`make e2e-spine` runs `testsprite_tests/TC000_Full_User_Journey.py`, which assumes the servers from terminals 1 and 2 are already running. A passing run proves the end-to-end login → dashboard → new case → upload document flow still works.

Use this procedure whenever you need a clean environment for the canonical journey or when validating future feature work against the golden path.
