# Roadmap & Phases (Post-M4.1)

## 1) High-Level Vision
- Canada Immigration OS with transparent, explainable rule engine.
- Config-first: IRCC rules live in `config/domain/*.yaml`; code reads, never hard-codes thresholds.
- Domain knowledge → config → rule engine → APIs → UI; AI/co-pilot agents later for config, product, and case guidance.
- Backend-first, API-led; frontend surfaces are thin, explainable, and read-only until governance allows edits.

## 2) Phase Map (Top-Level)
- **Phase 0 – Foundations & Discovery (✅ Done)**: Competitor research, PRD, risk analysis, spec refinement.
- **Phase 1 – Domain Knowledge Ingestion (✅ Done for core EE)**: CRS, CLB tables, program rules (FSW/CEC/FST), PoF, NOC/TEER, biometrics/medicals, ADR patterns.
- **Phase 2 – Rule Engine & Config Layer (✅ Done)**: ConfigService, CRS engine, program eligibility, document matrix, Case Evaluation API.
- **Phase 3 – Initial UX & Admin Surfaces (✅ Done)**: Admin Config API & UI (read-only); Case Intake UI (`/express-entry/intake`); roadmap doc created in M3.4.
- **Phase 4 – Persistence, Pricing & Accounts (🟡 In Progress)**: M3.5 Case History & Audit ✅; M4.1 Case Lifecycle & Tenant Infrastructure ✅; next up M4.2 Pricing Plans & Case Types.
- **Phase 5 – AI Agent Layer & Automation (🔵 Planned)**: Product agent, Configurator agent, Case coach, QA agent; OpenHands/Cursor integration for continuous improvement.
- **Phase 6 – Production Hardening & Scale (🔵 Planned)**: Load tests, observability, incident playbooks, performance tuning.

## 3) Where We Are Today
- Post-**Phase 4.1**: Case History & Audit (M3.5) and Case Lifecycle + Tenant Infrastructure (M4.1) are live with snapshots/events and tenant-aware ownership.
- Entering **Phase 4** execution focused on pricing/accounts; next concrete build step is **M4.2 – Pricing Plans & Case Types**.

## 4) Next Milestones (3–5)
- **M3.5 – Case History & Audit**: ✅ Persist evaluations with CaseRecord/Snapshot/Event, audit log, and history API.
- **M4.1 – Case Lifecycle & Tenant Infrastructure**: ✅ Tenant/User models, lifecycle service + API with snapshots/events.
- **M4.2 – Pricing Plans & Case Types**: Plan selection, case type catalog, and paywall hooks around evaluations (next in queue).
- **M5.1 – Configurator AI Agent (read-only suggestions)**: Surface suggested config diffs; no auto-write.
- **M5.2 – OpenHands-assisted refactor & deeper tests**: Hardening of rule engine + UI with automated refactors/tests.

