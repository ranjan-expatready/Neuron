# PRODUCT LOG

## Status Legend

- ✅ Done — Designed, implemented, and covered by tests/runbooks
- 🟡 Partial / In Progress — Some components exist but blueprint scope not met
- 🔴 Missing — Not implemented in code base yet
- 🔵 Planned — Scheduled in roadmap but no execution started

## A. Platform & Core App

- ✅ Backend runtime, tooling & CI parity (`backend/Makefile`, `backend/.venv`, `docs/E2E_SPINE_SETUP.md`) – Python 3.10.19 toolchain, pytest spine, and e2e helpers aligned with `[BP-07]`.
- ✅ Canonical FastAPI surface (`backend/src/app/main.py`, `backend/src/app/api/*`) – Auth, organizations, cases, and documents online per `[BP-03]`.
- ✅ Multi-tenant data model & tenancy guardrails (`backend/src/app/models/*`, Alembic) – Auth binding across case APIs, strict tenant isolation on CaseRecord/Snapshot/Event, lifecycle RBAC, soft deletes with retention stub, standardized security errors (M4.3).
- ✅ M4.3 Security Guardrails – RCICs and tenants are protected by enforced auth/tenant scoping, role-based lifecycle controls, soft deletes by default, and consistent security error responses.
- 🔴 Observability, metrics & SRE stack (logs, tracing, incident runbooks) – Logging strategy outlined in `[BP-05]/[BP-07]` but no implementation yet.
- 🔴 Mobile & offline-ready client surfaces – Blueprint `[BP-04]/[BP-13]` calls for responsive & native experiences that are not in the repo.

## B. Users, Organizations & Access

- ✅ Authentication & session flows (`backend/src/app/api/routes/auth.py`, `frontend/src/lib/auth-context.tsx`) – JWT login and dashboard redirect are stable.
- 🟡 Organization + membership management (`backend/src/app/api/routes/organizations.py`) – Server CRUD exists; UI switching, invitations, and approval workflows unfinished `[BP-03]`.
- 🔴 Fine-grained RBAC & entitlement matrix – Role catalog defined in `[BP-04]`, but enforcement middleware/UI absent.
- 🔴 Compliance-grade audit logging & session history (`BP-05`, `BP-10`) – No immutable audit tables or reviewer tools yet.
- 🔴 Multi-language/localization + accessibility (`BP-13` P1) – Internationalization requirements documented but not implemented in web app.

## C. Core Immigration OS Features

- ✅ Case lifecycle management (`backend/src/app/api/routes/cases.py`, `frontend/src/app/cases/*`) – Creation, status updates, and document tabs online per `[BP-03]`.
- ✅ Document intake & storage (`backend/src/app/api/routes/documents.py`, `frontend/src/app/cases/[id]/upload/page.tsx`) – Secure uploads with categorization, partial OCR hooks.
- 🟡 Person/client profiles – Backend models exist, but dedicated UI journeys, household management, and profile completeness scoring remain `[BP-02]/[BP-03]`.
- 🟡 Workflow & task service – Test plan + scaffolding exist (`docs/WORKFLOW_TASK_TEST_PLAN.md`), yet services/routes aren’t production-ready `[BP-08]`.
- 🟡 Billing plan enforcement stub (M4.5) – Plan config + tenant billing state, plan limits on case creation/evaluation/lifecycle, admin usage endpoints; payments/trust accounting still pending `[BP-03 §5.3]`.
- 🔴 Lead/CRM pipeline → case automation – Intake flows remain manual despite `[BP-13 §Phase 2]`.

## D. Brain & AI (Law, Rules, CRS, Intelligence)

- 🟡 CRS engine core (Express Entry) – Config-first CRS computation with structured factor breakdown shipped backend-only (no UI/case wiring yet).
- 🟡 M5.2 Structured CRS explainability – Each CRS factor now returns machine-readable explanation metadata (codes, rule paths, input/threshold summaries); no NL/UI yet.
- 🟡 M5.3 Natural-language CRS explanations & case integration – CRS engine now emits human-friendly titles/descriptions from structured explanations and exposes CRS + explanations in case evaluation responses and history snapshots.
- 🔴 Law intelligence & rule ingestion – Monitoring/approved-rules engine from `[BP-09]` not implemented.
- 🔴 Advisory playbooks & compliance guidance – Blueprint `[BP-10]` artifacts exist only in docs.
- 🔴 Client success / 24×7 support agent – No runtime or UI instrumentation yet `[BP-09]`.
- 🔵 Document intelligence + AI explainability – Planned via Phase 2 `[BP-13]`; current document service is rule-based only.
- ✅ Config-first domain layer (`config/domain/*.yaml`) established as the canonical source for immigration rules (CRS, eligibility, documents). Code must not hard-code thresholds; configs drive future engines.
- ✅ Domain ConfigService (Milestone 2.1) — backend service loads typed `config/domain/*.yaml` bundle for rule engine and future admin tools.
- ✅ Program Eligibility Engine (Milestone 2.2) — config-driven evaluation for FSW/CEC/FST wired through ConfigService + RuleEngineService with unit tests.
- ✅ Milestone 2.3 — Document & Forms Matrix + Case Skeleton (backend-only): config-driven forms/documents resolution and case assembly using RuleEngineService + DocumentMatrixService.
- ✅ Milestone 2.4 — Case Evaluation API & Explainability: POST `/api/v1/cases/evaluate` exposes program eligibility, CRS breakdown, and documents/forms with config hashes; backend-only, config-driven.
- ✅ Milestone 3.1 — Admin Config Read API: read-only endpoints expose loaded domain configs (CRS, language, work, PoF, programs, arranged employment, biometrics/medicals, documents/forms) for admin/agent introspection; config-first, backend-only.
- ✅ Milestone 3.2 — Admin Config UI (read-only): frontend route `/admin/config` displays section list and JSON snapshots from Admin Config API; mock fallback for dev when API is unavailable; no edits.
- ✅ Milestone 3.3 — Express Entry Case Intake UI: frontend route `/express-entry/intake` collects minimal profile inputs, calls Case Evaluation API, and displays program eligibility, CRS breakdown, and required forms/documents (read-only, single-session).
- ✅ Milestone 3.4 — Roadmap & Phase Overview: added `docs/ROADMAP_AND_PHASES.md` summarizing phases 0–6, current position (end of Phase 3.3), and next milestones; linked in knowledge base.
- ✅ Rule engine skeleton + config wiring (ENG-RULE-001/002) merged: CRS/eligibility engine reads `config/domain/*.yaml`; still internal-only, no public API exposure yet.
- ✅ Milestone 3.5 – Case History, Audit & Versioned Snapshots
  - Implemented CaseRecord, CaseSnapshot, and CaseEvent models with Alembic migration.
  - Case Evaluation API now persists evaluations and returns `case_id` + `version` with audit metadata.
  - Added internal Case History API (`/api/v1/case-history`) for listing and inspecting stored cases.
- Phase 5 Golden Snapshot (integration/phase5_crs_and_billing): billing plan enforcement + CRS core + structured/NL explainability are integrated and tested; case evaluation returns explainable CRS breakdown, suitable for RCIC-facing backend flows (UI/report surfacing remains future).
- ✅ Milestone 4.1 – Case Lifecycle & Tenant Infrastructure
  - Added Tenant and tenant-scoped User models (composite tenant+email uniqueness, roles, hashed_password).
  - CaseRecord now tracks tenant ownership, creator user, and lifecycle status; snapshots/events store tenant_id.
  - Case lifecycle service + API (`/api/v1/case-lifecycle/*`) manage submit/review/complete/archive with audit + snapshots; docs/tests updated.
- 🔵 M6.1 Intake/Document/Form design foundation added (docs/INTAKE_AND_DOCUMENT_MODEL.md + config stubs for fields/intake templates/document definitions/form mappings); no runtime behavior change. Wiring planned for M6.2+.
- 🟡 M6.2 Intake/Document engine (backend): added validated config loaders, `/api/v1/intake-schema` for program intake templates, and `/api/v1/document-checklist/{case_id}` for config-driven checklists. UI wiring remains pending in M6.3.
- 🟡 M6.3 RCIC Intake UI: schema-driven intake page renders steps/fields from `/api/v1/intake-schema`, saves intake data to case form data, and shows document checklist from `/api/v1/document-checklist/{case_id}`. Client self-serve/mobile will reuse the same schema in future milestones.
- 🟢 M6.3h Intake hardening: RCIC intake uses canonical profile API (`/api/v1/cases/{case_id}/profile`), select options pulled from config-backed `/api/v1/intake-options`, and document checklist displays upload status by cross-referencing case documents.
- 🟢 M6.4 Client self-serve intake portal: client-facing intake page renders schema from `/api/v1/intake-schema`, reads/writes canonical profile via `/api/v1/cases/{case_id}/profile`, and surfaces document checklist with upload status using existing case documents API.
- 🟢 M7.1 Admin Config Console (read-only): new admin APIs under `/api/v1/admin/intake/*` expose field dictionary, templates, documents, forms, and options; admin UI pages under `/admin/config/intake` let RCIC/admin users inspect active config (no editing).
- 🟢 M7.2 Intake config drafts (non-live): DB-backed draft layer and admin APIs/UI (`/api/v1/admin/intake/drafts`, `/admin/config/intake/drafts`) allow creating/updating/archiving draft fields/templates/documents/forms. Runtime still driven by YAML; activation/approval in M7.3.
- 🟢 M7.3 Intake config approval & activation: Status transitions (draft → in_review → active → retired/rejected), admin-only activation endpoints/UI, and runtime override layer that merges ACTIVE drafts on top of YAML for fields/templates/documents/forms. Retired/rejected drafts remain historical only.

## E. Agentic & Automation Features

- 🟡 Workflow/task automation scaffolding – Backlog + test plan exist, but automation loops are not wired end-to-end `[BP-08]`.
- 🟢 M8.0 Agentic Platform Skeleton: agent sessions/actions DB + migration, AgentOrchestratorService, ClientEngagementAgent (suggestions only, no sends), admin APIs `/api/v1/admin/agents/actions`/`sessions/{id}`, admin UI `/admin/agents` for audit visibility.
- 🟢 M8.1 Client Engagement Agent Spec (Hybrid Mode): design covering shadow vs auto modes, event triggers, safety/guardrails, memory model, data contracts, and workflows. No runtime behavior changes yet; implementation follows in M8.2+.
- 🟢 M8.2 Client Engagement Agent (shadow mode): template-based suggestions for intake incomplete, missing documents, and client questions; admin-triggered APIs and case engagement UI; no auto-send, no LLM.
- 🟢 M8.3 Client Engagement Agent (LLM-assisted shadow replies): LLM-assisted draft replies for client questions and optional reminder rewrites; template fallback if LLM disabled/unavailable; admin-triggered only; no auto-send/cron; strict guardrails.
- 🟢 M8.4 Client Engagement AUTO mode (limited): tenant-controlled toggles and throttling for intake/doc reminders; admin-triggered auto-run endpoint; executed actions logged with `auto_mode=true`; client questions remain shadow-only; no internal cron added.
- 🟢 Tagged `v0.8.3-phase8-agentic-shadow` after M8.3: Phase 8 golden snapshot with shadow + LLM drafts, full backend/frontend tests passing.
- 🟢 M9.1 Document Reviewer Agent (shadow-only): Backend agent + admin endpoint to suggest required_present/required_missing/duplicates/unmatched using document matrix + case documents (metadata only); RCIC UI tab to run/view reviews; SHADOW-only, no sends or state mutation.
- 🟢 M9.2 Document Reviewer Agent (shadow-only, OCR-aware optional): DocumentContentService abstraction; optional OCR/PDF-aware extraction adds content warnings; matrix remains source of truth; no AUTO, no external sends; RCIC UI surfaces warnings.
- 🟢 Tagged `v0.9.2-phase9-doc-review`: Phase 9 document review golden snapshot (Document Reviewer Agent with metadata + optional OCR content checks, shadow-only, RCIC-facing).
- 🟢 M9.3 Document Heuristics Engine (shadow-only): Deterministic heuristics over OCR text + metadata (missing keywords, misplaced hints, expiry filename heuristics, low-quality signals, simple profile consistency). Findings are SHADOW-only and surfaced in admin/RCIC UI; no sends or state mutation.
- 🟢 Tagged `v0.9.3-phase9-doc-review-heuristics`: Updated Phase 9.3 golden snapshot with metadata + optional OCR + deterministic heuristics; shadow-only, RCIC-facing, non-destructive.
- 🟢 M10.1 Form Autofill & Submission Architecture (docs-only): Architecture/spec for form autofill and IRCC submission prep (config-first form definitions/mappings, shadow-mode agents, safety, APIs, phasing). No runtime changes; foundation for M10.2+.
- 🟢 M10.2 Form config schemas & loaders (backend-only): Added config/domain form definitions/mappings/bundles plus Pydantic-backed loaders with cross-reference validation; foundation only (no FormAutofillEngine/APIs/UI); tests cover happy path and invalid references.
- 🟢 M10.3 FormAutofillEngine (backend-only preview): Service builds FormAutofillPreviewResult from configs + canonical profile; no DB mutations, no public API/UI, no PDFs/web automation.
- 🟢 M10.4 Forms Autofill Preview (RCIC API + UI): Added read-only GET `/api/v1/cases/{case_id}/forms/autofill-preview` (tenant/RBAC-protected) and RCIC page `/cases/[caseId]/forms-autofill` to display FormAutofillEngine output. No PDFs or submissions; clearly labeled as draft/preview.
- 🟢 Tagged `v0.10.4-phase10-forms-autofill-preview`: Phase 10 golden snapshot for M10.4 forms autofill preview (API + RCIC UI, read-only). Tests: backend pytest 275 collected / 271 passed / 4 skipped, coverage 86.88%; frontend jest 10/10 suites, 16/16 tests passed.
- 🟢 M11.1 Submission Readiness Report (backend-only): Deterministic `SubmissionReadinessService` + Pydantic models to compute per-form completion, blockers (missing required fields/docs), and warnings (confirmation needed) using FormAutofillEngine + document matrix. API GET `/api/v1/cases/{case_id}/submission/readiness?bundle_id=...` (admin/owner/rcic) plus optional bundle listing `/api/v1/config/form-bundles`; read-only, no PDFs/submission. Tests: backend pytest 284 collected / 280 passed / 4 skipped; coverage 87.01%. Frontend unchanged.
- 🔴 Multi-agent orchestration runtime – Architecture described in `[BP-09]` yet no orchestration service or queue workers live (planned M8.2+).
- 🔴 Config/metadata agent + low-code builder – `[BP-03]/[BP-09]` specify dynamic config, still missing.
- 🔴 End-user automation UX – No surfaced agent suggestions, checklists, or automation toggles `[BP-03 §5.4]`.
- 🔵 Agent marketplace & extension SDK – Logged as Phase 3 `[BP-13]`, unstarted.

## F. DevOps, CI/CD & Reliability

- ✅ CI guardrails + branch protection (`backend-tests`, `frontend-tests`) – Required on `main`, `.env` provisioning fixed, documented in `docs/ENGINEERING_GOVERNANCE.md`.
- ✅ Engineering governance + persistent memory – Mandatory bootstrap/log loop enforced via `.ai-memory/ENGINEERING_LOG.md`.
- 🟡 Test infrastructure & TestSprite automation – Manual e2e spine works, but automated orchestration + coverage gating pending `[BP-11]`.
- 🔴 Observability & alerting – Metrics/log stacks described in `[BP-07]` and FAANG DevOps review; nothing deployed.
- 🔴 Data residency, backups & DR – Requirements captured in `[BP-05]/[BP-12]` but no infra automation yet.
- 🔵 Production deployment automation – Deployment runbooks exist, but no GitHub environments/K8s manifests checked in.

## G. Future Expansion & Go-To-Market

- 🔵 Integration marketplace & developer portal – Planned for Phase 2 `[BP-13 §Integrations]`.
- 🔵 Multi-language experiences (French, Mandarin, Hindi, etc.) – Documented need, no implementation `[BP-13 §Global]`.
- 🔵 Mobile apps (consultant + client) – Strategy defined in `[BP-13 P1]`, awaiting execution.
- 🔵 Partnership ecosystem & GTM motions – Outlined in `[BP-13]/spec gap #24` but tooling/support absent.
- 🔵 International expansion (UK/AUS/US playbooks) – Captured in `[BP-13 Phase 3]`, unstarted.

## 2025-12-09 – M4.4 Observability & SRE Baseline
- Added request ID middleware and structured logging with tenant/user context across case evaluation, lifecycle, history, and admin config flows.
- Exposed internal liveness/readiness (`/internal/healthz`, `/internal/readyz`) and metrics (`/internal/metrics`) endpoints for ops use.
- Established in-process request counters to support future telemetry integration.
