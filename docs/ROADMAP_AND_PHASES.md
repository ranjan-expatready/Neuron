# Roadmap & Phases (M3.4 – Docs Only)

## 1) High-Level Vision
- Canada Immigration OS with transparent, explainable rule engine.
- Config-first: IRCC rules live in `config/domain/*.yaml`; code reads, never hard-codes thresholds.
- Domain knowledge → config → rule engine → APIs → UI; AI/co-pilot agents later for config, product, and case guidance.
- Backend-first, API-led; frontend surfaces are thin, explainable, and read-only until governance allows edits.

## 2) Phase Map (Top-Level)
- **Phase 0 – Foundations & Discovery (✅ Done)**: Competitor research, PRD, risk analysis, spec refinement.
- **Phase 1 – Domain Knowledge Ingestion (✅ Done for core EE)**: CRS, CLB tables, program rules (FSW/CEC/FST), PoF, NOC/TEER, biometrics/medicals, ADR patterns.
- **Phase 2 – Rule Engine & Config Layer (✅ Done)**: ConfigService, CRS engine, program eligibility, document matrix, Case Evaluation API.
- **Phase 3 – Initial UX & Admin Surfaces (🟡 In Progress)**: Admin Config API & UI (read-only); Case Intake UI (`/express-entry/intake`). Next: minimal case history, basic UX polish.
- **Phase 4 – Persistence, Pricing & Accounts (🔵 Planned)**: User accounts, saved cases, pricing/plans, billing integration.
- **Phase 5 – AI Agent Layer & Automation (🔵 Planned)**: Product agent, Configurator agent, Case coach, QA agent; OpenHands/Cursor integration for continuous improvement.
- **Phase 6 – Production Hardening & Scale (🔵 Planned)**: Load tests, observability, incident playbooks, performance tuning.

## 3) Where We Are Today
- Currently at end of **Phase 3.3**: Admin Config UI + Case Intake UI are live; backend rule engine + configs are wired and tested.
- Phase 3.4 (this doc) is roadmap/orientation.
- Next concrete build step: **Phase 3.5 – Case History & Minimal Persistence** (planned).

## 4) Next Milestones (3–5)
- **M3.5 – Case History (Local & API-ready)**: Minimal persistence for evaluated cases; history list + recall.
- **M4.1 – Accounts & Auth Skeleton**: Basic account flows to gate case history and admin tools.
- **M4.2 – Pricing Plans & Case Types**: Plan selection + paywall hooks around evaluations.
- **M5.1 – Configurator AI Agent (read-only suggestions)**: Surface suggested config diffs; no auto-write.
- **M5.2 – OpenHands-assisted refactor & deeper tests**: Hardening of rule engine + UI with automated refactors/tests.


