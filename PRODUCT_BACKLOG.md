# PRODUCT_BACKLOG

## 1. Overview

This backlog synthesizes blueprint packets `[BP-00…BP-14]`, the refined PRD, and the implementation gap analysis into a single, version-controlled source of truth. Every 🔴 **Missing** or 🟡 **Partial** capability from the blueprints now maps to a concrete backlog ID so engineers, product, and agents can reference the same plan before opening a PR.

## 2. Backlog Conventions

- **Status:** 🔴 Missing (no code) or 🟡 Partial (scaffolding exists but not blueprint-complete).
- **Priority:** HIGH / MEDIUM / LOW, mirroring gap-analysis urgency.
- **Phase:** P1 Foundation, P2 Growth, P3 Scale (from `[BP-13]` roadmap).
- **Type:** Primary execution lane (Backend API, Frontend UX, AI/Agent, Infra, etc.).
- **Source:** Pointer to blueprint / PRD / gap-analysis sections that define the requirement.
- **Dependencies:** Upstream services or artifacts that must exist before this backlog item can ship.

## 3. Backlog by Domain

### 3.1 Platform & Core

#### [PL-001] Multi-tenant Data Isolation Hardening

- **Domain:** 3.1 Platform & Core
- **Status:** ✅ Done (M4.3)
- **Priority:** HIGH
- **Phase:** P1 (Foundation)
- **Type:** Database + Backend services
- **Description:** Auth binding on case APIs, strict tenant isolation on CaseRecord/Snapshot/Event, lifecycle RBAC, soft deletes + retention stub, standardized security errors. Remaining: production retention purge policies and RLS/backup automation (future).
- **Source:** BP-06 (Data Model & ERD), BP-14 (Gap #10)
- **Dependencies:** Alembic migrations, tenancy middleware, org context propagation

#### [PL-002] Observability & Metrics Stack

- **Domain:** 3.1 Platform & Core
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Infra / DevOps
- **Description:** Implement logging, metrics, traces, SLIs/SLOs, and incident runbooks (Prometheus, Grafana, OpenTelemetry) as mandated by `[BP-05]/[BP-07]`.
- **Source:** BP-05 (Non-Functional Requirements), BP-07 (System Architecture)
- **Dependencies:** Centralized logging pipeline, deployment automation

#### [PL-003] Scalability Architecture Guardrails

- **Domain:** 3.1 Platform & Core
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Architecture
- **Description:** Define and codify autoscaling policies, caching, sharding, CDN usage, and performance budgets per `[BP-07]` & Gap #10, then bake into IaC.
- **Source:** BP-07, BP-14 Gap #10
- **Dependencies:** Infra-as-code repo, observability stack

#### [PL-004] API Design Standards & Versioning

- **Domain:** 3.1 Platform & Core
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend API Governance
- **Description:** Publish OpenAPI specs, introduce semantic versioning, rate limiting, and REST/GraphQL guidelines so integrations align with `[BP-03]/[BP-07]` requirements.
- **Source:** BP-03 (Feature Catalog), BP-14 Gap #11
- **Dependencies:** API gateway, documentation tooling

#### [PL-005] Mobile & Offline-Ready Core Surfaces

- **Domain:** 3.1 Platform & Core
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P2 (Growth)
- **Type:** Frontend + Mobile
- **Description:** Deliver responsive + native client/consultant experiences (offline cache, push notifications, camera capture) as specified in `[BP-04]/[BP-13]`.
- **Source:** BP-04 (Functional Requirements), BP-13 Phase 2
- **Dependencies:** Mobile design system, API standards, authentication upgrades

#### [PL-006] Search & Discovery Service

- **Domain:** 3.1 Platform & Core
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Backend Service
- **Description:** Implement Elasticsearch/Semantic search across cases, persons, documents, and knowledge base with facets and analytics `[BP-07]`.
- **Source:** BP-07 (Architecture), BP-14 Gap #15
- **Dependencies:** Data indexing pipeline, observability, API standards

### 3.2 Users & Access

#### [UA-001] Fine-Grained RBAC & Entitlement Matrix

- **Domain:** 3.2 Users & Access
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend + Frontend
- **Description:** Implement the role catalog, field-level permissions, and enforcement middleware defined in `[BP-04]`, including admin UX for grants.
- **Source:** BP-04 (Functional Requirements), BP-14 Gap #11
- **Dependencies:** Org membership service, audit logging

#### [UA-002] Org Membership UI & Approval Workflows

- **Domain:** 3.2 Users & Access
- **Status:** 🟡 Partial
- **Priority:** MEDIUM
- **Phase:** P1
- **Type:** Frontend UX
- **Description:** Complete invitations, approvals, role switching, and org dashboards so consultants can manage teams per `[BP-03 §5.2]`.
- **Source:** BP-03 (Feature Catalog), PRD §5.1.2
- **Dependencies:** RBAC, notification service

#### [UA-003] Compliance-Grade Audit Logging

- **Domain:** 3.2 Users & Access
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend / Infra
- **Description:** Build immutable audit tables, export pipelines, and reviewer UI to meet Law Society + IRCC obligations `[BP-05]/[BP-10]`.
- **Source:** BP-05 (NFR), BP-10 (Legal & Compliance)
- **Dependencies:** Observability stack, RBAC

#### [UA-004] Localization & Accessibility Framework

- **Domain:** 3.2 Users & Access
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Frontend
- **Description:** Add i18n pipelines, translation management, RTL support, and WCAG 2.1 AA conformance `[BP-13]`.
- **Source:** BP-13 (Future Backlog), BP-14 Gap #19
- **Dependencies:** Design system, content strategy

#### [UA-005] Secure Client Onboarding & eKYC

- **Domain:** 3.2 Users & Access
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend + Frontend
- **Description:** Build onboarding wizard with identity verification, consent capture, and AML/KYC checks `[BP-04 §Client Portal]`.
- **Source:** BP-04, BP-14 Gap #20
- **Dependencies:** Payment service, audit logging, document workflows

### 3.3 Cases & Workflows

#### [CF-001] Workflow & Task Service GA

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🟡 Partial
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend API + Scheduler
- **Description:** Finish case-task models, lifecycle hooks, reminders, and ATDD suite so automation unblocks `[BP-08]`.
- **Source:** BP-08 (Workflows), WORKFLOW_TASK_TEST_PLAN.md, BP-14 Gap #1
- **Dependencies:** Notification service, org context, TestSprite plan

#### [CF-002] Checklist Automation & Templates

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend + Frontend
- **Description:** Deliver dynamic checklists per case type, including template builder, reminder cadence, and compliance attestations `[BP-03 §5.4]`.
- **Source:** BP-03, BP-08
- **Dependencies:** Workflow service, Config agent

#### [CF-003] Billing, Payments & Trust Accounting

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🟡 Partial
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend + Integrations
- **Description:** Implement invoices, payment plans, trust account handling, and PCI/AML compliance `[BP-03 §5.3]`. Plan enforcement + usage tracking shipped in M4.5; payments/trust accounting remain.
- **Source:** BP-03, BP-14 Gap #21, #20
- **Dependencies:** Payment gateway, audit logging, reporting

#### [CF-004] Lead-to-Case CRM Automation

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Backend + Frontend
- **Description:** Connect lead scoring, intake forms, and automated case creation with nurturing flows `[BP-13 §Phase 2]`.
- **Source:** BP-13, PRD §5.2.1
- **Dependencies:** CRM service, communication hub

#### [CF-005] SLA & Compliance Monitors

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Backend Service
- **Description:** Build real-time SLA tracking, deadline alerts, and compliance dashboards for IRCC obligations `[BP-10]`.
- **Source:** BP-10 (Legal), BP-11 (Test Strategy)
- **Dependencies:** Workflow events, reporting engine

#### [CF-006] Unified Client Communication Hub

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Frontend + Integrations
- **Description:** Deliver omnichannel messaging (email, SMS, chat, video) with templates and history `[BP-03 §5.5]`.
- **Source:** BP-03, Gap Analysis #9
- **Dependencies:** Notification service, audit logging, CRM

#### [INT-001] Intake config loaders & validators (M6.2)

- **Domain:** 3.3 Cases & Workflows
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend rules/config
- **Description:** Implement typed loaders/validators for fields, intake templates, documents, and forms configs; expose read-only bundles for rule engine, checklists, and UI rendering.
- **Dependencies:** Config schemas, config/domain stubs, ConfigService patterns.

#### [INT-002] Intake template & checklist APIs (M6.2)

- **Domain:** 3.3 Cases & Workflows
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend API
- **Description:** Add APIs to serve intake templates and document checklists derived from canonical intake/document configs; no persistence yet.
- **Dependencies:** INT-001 loaders, Case Evaluation API patterns.

#### [INT-003] Schema-driven intake UI (M6.3)

- **Domain:** 3.3 Cases & Workflows
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Frontend UX
- **Description:** Update RCIC/client portal intake to render dynamically from intake templates and field dictionary; reuse canonical profile data across cases.
- **Dependencies:** INT-001/INT-002, CASE_INTAKE_UI baseline.

#### [INT-004] Admin Config UI for intake/doc/forms (M6.X)

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🔵 Planned
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Frontend/Admin
- **Description:** Build admin UI for proposing/reviewing intake fields, templates, documents, and forms with human approval workflow and versioning.
- **Dependencies:** Admin Config read API, governance rules, approval backend.

#### [INT-005] Seed IRCC form mappings (IMM series) (M6.X)

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🔵 Planned
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Backend rules/config
- **Description:** Add initial mappings for IMM0008/IMM5669/IMM5406 and related forms referencing canonical fields; keep draft until validated.
- **Dependencies:** INT-001 loaders, form definitions, domain knowledge for form fields.

### 3.4 Documents & OCR

#### [DO-001] Document Intelligence Agent MVP

#### [INT-006] Client self-serve intake portal (M6.4+)

- **Domain:** 3.3 Cases & Workflows
- **Status:** ✅ Done (baseline portal)
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Frontend UX
- **Description:** Client-facing intake uses the same schema-driven renderer, supports authentication, and saves canonical profile data for reuse.
- **Dependencies:** INT-003, backend profile persistence APIs.

#### [INT-007] Checklist ↔ upload integration (M6.4+)

- **Domain:** 3.3 Cases & Workflows
- **Status:** ✅ Done (status surfaced; richer UX pending)
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Frontend/Backend
- **Description:** Tie document checklist items to upload widgets, show completion state, and surface required/optional statuses from checklist.
- **Dependencies:** INT-002, document upload APIs.

#### [INT-008] Admin Config UI + approval (M6.X)

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🔵 Planned
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Frontend/Admin
- **Description:** Build admin UI and approval flow for intake fields/templates/documents/forms; enforce human-in-loop before activation.
- **Dependencies:** INT-001/002, governance rules.

#### [INT-009] Extended condition operators (M6.X)

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🔵 Planned
#### [INT-010] Canonical profile API wiring (M6.3h)

- **Domain:** 3.3 Cases & Workflows
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend/API
- **Description:** Expose GET/PATCH `/cases/{case_id}/profile`, map intake data paths to canonical profile, and use it as the system-of-record for intake.

#### [INT-011] Intake options from config (M6.3h)

- **Domain:** 3.3 Cases & Workflows
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend/Frontend
- **Description:** Options resolved from config via `/api/v1/intake-options` and hydrated into intake schema/UI.

#### [INT-012] Checklist upload status surfacing (M6.3h)

- **Domain:** 3.3 Cases & Workflows
- **Status:** ✅ Done (status surface; richer UX pending)
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Frontend
- **Description:** Document checklist displays uploaded/missing using case documents API; link to upload workflow to be expanded in M6.4.

#### [INT-013] Client UX polish & mobile readiness (M6.5+)

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🔵 Planned
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Frontend UX
- **Description:** Improve client portal styling, responsive/mobile layout, and wizard-like program selection; add clearer guidance per document item.

#### [INT-014] Rich upload management (M6.5+)

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🔵 Planned
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Frontend/Backend
- **Description:** Upload previews, status badges, deletion/re-upload, and progress; sync checklist state in real time.

#### [INT-015] Program selection wizard (M6.5+)

#### [CFG-006] Admin Config Console (read-only) (M7.1)

- **Domain:** Admin / Config
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend + Frontend
- **Description:** Read-only admin APIs (`/api/v1/admin/intake/*`) and UI under `/admin/config/intake` to inspect field dictionary, intake templates, documents, forms, and option sets.

#### [CFG-007] Admin config editing (draft) (M7.2)

- **Domain:** Admin / Config
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend + Frontend
- **Description:** Allow creating/updating config entries in draft state via secured admin APIs; no activation without approval.

#### [CFG-008] Admin config approval workflow (M7.3)

- **Domain:** Admin / Config
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend + Frontend
- **Description:** Draft → in_review → active → retired workflow with audit trail, role-based approvals, and status transition APIs/UI (submit, reject, activate, retire).

#### [CFG-010] Draft activation pipeline (M7.3)

- **Domain:** Admin / Config
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend
- **Description:** Runtime override layer merges ACTIVE drafts over YAML for intake fields/templates/documents/forms; retired/rejected drafts are ignored; activation records approver + timestamp.

#### [CFG-009] AI-assisted config proposals (M7.4)

- **Domain:** Admin / Config
- **Status:** 🔵 Planned
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** AI/Backend
- **Description:** AI suggests config diffs from `domain_knowledge`/IRCC PDFs; proposals stored as drafts awaiting human approval.

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🔵 Planned
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Frontend UX
- **Description:** Client-friendly program selection/confirmation with guardrails and plan awareness before rendering intake schema.
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Backend rules/config
- **Description:** Add richer condition operators (lt/lte/range/regex) and nested logical groups for document/intake visibility.
- **Dependencies:** INT-001/002, config schema updates, tests.

- **Domain:** 3.4 Documents & OCR
- **Status:** 🟡 Partial
- **Priority:** HIGH
- **Phase:** P1
- **Type:** AI/Agent + Backend
- **Description:** Extend current OCR hooks into full classification/validation agent with explainable checks `[BP-03 §5.2]`.
- **Source:** BP-03, BP-09 §Document Intelligence
- **Dependencies:** Document storage, AI runtime, audit logging

#### [DO-002] E-Signature Integration

- **Domain:** 3.4 Documents & OCR
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Integration
- **Description:** Integrate DocuSign/HelloSign with workflows, audit trails, and reminders `[BP-03 §5.3]`.
- **Source:** BP-03, BP-14 Gap #3
- **Dependencies:** Document templates, billing

#### [DO-003] Advanced Document Automation Suite

- **Domain:** 3.4 Documents & OCR
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Backend + Frontend
- **Description:** Add conditional templates, mail merge, version control, and approvals `[BP-03 §5.2]`, Gap #8.
- **Source:** BP-03, BP-14 Gap #8
- **Dependencies:** Config agent, document intelligence

#### [DO-004] Document Comparison & Redaction Tools

- **Domain:** 3.4 Documents & OCR
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Backend + Frontend
- **Description:** Provide diffing, automated redaction, and share-safe exports for legal reviews `[BP-03]`.
- **Source:** BP-03, Gap Analysis #8
- **Dependencies:** Document storage, audit logging

### 3.5 Agentic Platform (Phase 8)

#### [AGENT-001] Agentic platform skeleton (M8.0)

- **Domain:** Agentic / Automation
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend + Frontend
- **Description:** Agent sessions/actions models + migration; AgentOrchestratorService; ClientEngagementAgent skeleton (suggestions only); admin APIs `/api/v1/admin/agents/*`; admin UI `/admin/agents`.

#### [AGENT-002] Client engagement LLM suggestions (M8.1)

- **Domain:** Agentic / Automation
- **Status:** 🔵 Planned
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend
- **Description:** Wire LLM-backed suggestions for client engagement with guardrails; keep audit logs; no auto-send without approval.

#### [AGENT-003] Event triggers for engagement (M8.1+)

- **Domain:** Agentic / Automation
- **Status:** 🔵 Planned
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend
- **Description:** Safe triggers (intake incomplete, missing docs) that enqueue agent suggestions without sending; admin controls and audits.

#### [AGENT-004] Document Reviewer Agent skeleton (M8.2)

- **Domain:** Agentic / Automation
- **Status:** 🔵 Planned
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Backend
- **Description:** Agent skeleton for doc review/quality flags; logs-only; no auto decisions.

#### [AGENT-005] Agent analytics dashboard (M8.2)

- **Domain:** Agentic / Automation
- **Status:** 🔵 Planned
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Frontend
- **Description:** Aggregate agent sessions/actions by tenant/case; charts, filters, export.

#### [AGENT-010] Client engagement shadow suggestions (M8.2)

- **Domain:** Agentic / Automation
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend + Frontend
- **Description:** Implement event ingestion and template-based shadow suggestions for client engagement; RCIC review/approve only; no auto-send.

#### [AGENT-011] LLM-based reply generation with guardrails (M8.3)

- **Domain:** Agentic / Automation
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend
- **Description:** Add LLM-backed suggestions for client engagement replies with strict guardrails (risk filters, RCIC approval).

#### [AGENT-012] AUTO mode configuration and rollout (M8.4)

- **Domain:** Agentic / Automation
- **Status:** 🔵 Planned
- **Priority:** HIGH
- **Phase:** P2
- **Type:** Backend + Frontend
- **Description:** Tenant-configurable AUTO mode for low-risk reminders (intake/docs), channel controls, frequency caps, full audit logging.

#### [DO-005] Multi-Language OCR & Classification

- **Domain:** 3.4 Documents & OCR
- **Status:** 🟡 Partial
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** AI/Agent
- **Description:** Expand OCR beyond English (French, Mandarin, Hindi, Spanish) with quality scoring `[BP-13]`.
- **Source:** BP-13 (Future Backlog), BP-03
- **Dependencies:** Document intelligence agent, localization framework

### 3.5 Brain & AI

#### [BA-001] CRS Core Calculator API

- **Domain:** 3.5 Brain & AI
- **Status:** ✅ Done (M5.1 core engine)
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend API + Rules Engine
- **Description:** Implement CRS scoring per current IRCC rules with unit/integration tests `[BP-03 §CRS]`. Config-first engine shipped backend-only; M5.2 delivered structured explainability; M5.3 delivered NL explanations and case integration (UI/report surfaces remain future).
- **Source:** BP-03, BP-09, BP-14 Gap #1
- **Dependencies:** Person profile schema, rule engine

#### [CFG-001] Domain Config Service (backend)

- **Domain:** 3.5 Brain & AI
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P1 (Foundation)
- **Type:** Backend Service
- **Description:** Implement a ConfigService to load/validate `config/domain/*.yaml` (CRS, programs, language, work, PoF, documents) with caching, versioning, and schema validation.
- **Source:** Config-first governance requirement
- **Dependencies:** YAML schema definitions, validation library, logging
- **Notes:** Backend ConfigService shipped in PR #22 (Milestone 2.1); backend consumers use the typed bundle; UI/admin surface remains future work.

#### [CFG-002] CI guard: ban hard-coded domain constants

- **Domain:** 3.5 Brain & AI
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P1
- **Type:** CI/DevEx
- **Description:** Add CI checks/lints to prevent hard-coded CRS/eligibility thresholds in backend/src and ensure domain logic reads from config/domain.
- **Source:** Config-first governance requirement
- **Dependencies:** ConfigService availability, lint/regex rules

#### [CFG-003] Admin Config UI (domain rules)

- **Domain:** 3.5 Brain & AI
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Frontend/Admin
- **Description:** Build an admin UI to edit `config/domain/*.yaml` with validation, preview, and staged rollout (draft/staging/prod).
- **Source:** Config-first governance requirement
- **Dependencies:** ConfigService API, authentication/authorization, validation APIs

#### [CFG-004] Admin Config Read API

- **Domain:** 3.5 Brain & AI
- **Status:** ✅ Done
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend API
- **Description:** Expose read-only domain configuration state (CRS, language, work_experience, proof_of_funds, program rules, arranged employment, biometrics/medicals, documents/forms) via `/api/v1/admin/config` for admins and AI config agents.
- **Dependencies:** ConfigService, DocumentMatrixService, `config/domain/*.yaml`

#### [CFG-005] Admin Config Write UI

- **Domain:** 3.5 Brain & AI
- **Status:** 🔵 Planned
- **Priority:** P2
- **Phase:** P2
- **Type:** Frontend/Admin
- **Description:** Add secure, audited editing capabilities to Admin Config UI (config change proposals, approvals, versioning).
- **Dependencies:** Admin Config Read UI, ConfigService API, auth/approvals

#### [UX-001] Case intake persistence & history

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🔵 Planned
- **Priority:** P2
- **Phase:** P2
- **Type:** Frontend/Backend
- **Description:** Allow authenticated users to save and revisit multiple case evaluations with history and comparisons.
- **Dependencies:** Case evaluation API, auth/session, storage

#### [UX-002] Pricing & checkout integration for case evaluation

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🔵 Planned
- **Priority:** P2
- **Phase:** P2
- **Type:** Frontend/Payments
- **Description:** Attach pricing plans and payment flow to case evaluation; gated access for paid tiers.
- **Dependencies:** Billing/payments service, auth, pricing config

#### [PM-001] Maintain roadmap and phases doc

- **Domain:** 3.5 Brain & AI
- **Status:** 🟡 In Progress
- **Priority:** P2
- **Phase:** P2
- **Type:** Product/Docs
- **Description:** Keep `docs/ROADMAP_AND_PHASES.md` aligned with major milestones; update after each phase change.
- **Dependencies:** Engineering governance, milestone tracking

#### [PM-002] Surface roadmap snapshot in admin/product UI

- **Domain:** 3.5 Brain & AI
- **Status:** 🔵 Planned
- **Priority:** P3
- **Phase:** P2
- **Type:** Frontend/Admin
- **Description:** Display a read-only roadmap/phase card in internal admin/product dashboard for quick orientation.
- **Dependencies:** Roadmap doc, admin UI

#### [BA-002] Eligibility What-If Simulator

- **Domain:** 3.5 Brain & AI
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P1
- **Type:** AI/Agent + Frontend
- **Description:** Provide multi-scenario planning, delta explanations, and saved recommendations `[BP-09]`.
- **Source:** BP-09 (AI Agents), PRD §5.1.1
- **Dependencies:** CRS calculator, case data, advisory UI

#### [BA-003] Law Intelligence & Rule Ingestion

- **Domain:** 3.5 Brain & AI
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P1
- **Type:** AI/Agent + Data Pipeline
- **Description:** Build ingestion for IRCC/PNP changes, approved rule storage, and human-in-loop approvals `[BP-09 §Law Intelligence]`.
- **Source:** BP-09, BP-10 (Compliance)
- **Dependencies:** Knowledge store, audit logging, notification service

#### [BA-004] Advisory Playbooks & Compliance Engine

- **Domain:** 3.5 Brain & AI
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** AI/Agent + UX
- **Description:** Encode advisory flows (checklists, prompts, playbooks) for law/compliance guidance `[BP-10]`.
- **Source:** BP-10, BP-13 Phase 2
- **Dependencies:** Rule engine, workflow service

#### [BA-005] Client Success AI Agent

- **Domain:** 3.5 Brain & AI
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** AI/Agent
- **Description:** Launch CSA for 24/7 communication, sentiment detection, and proactive nudges `[BP-09 §Client Success]`.
- **Source:** BP-09, PRD §4.1 Stage 4
- **Dependencies:** Communication hub, automation guardrails, localization

#### [BA-006] Policy Update Alerting & Impact Analysis

- **Domain:** 3.5 Brain & AI
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** AI/Agent + Reporting
- **Description:** Notify consultants when rule changes affect active cases, with impact scoring `[BP-09]`.
- **Source:** BP-09, BP-13
- **Dependencies:** Law intelligence ingestion, reporting engine

#### [IRCC-201] CRS CLB mappings

- **Domain:** 3.5 Brain & AI
- **Status:** 🟡 In Progress – CLB tables ingested; config wiring pending
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend rules/config
- **Description:** Add CLB-to-test score mapping tables (IELTS/CELPIP/TEF/TCF) to `config/domain/crs.yaml` and wire to CRS computation.
- **Dependencies:** Language test parser, config loader

#### [IRCC-202] CRS transferability tables

- **Domain:** 3.5 Brain & AI
- **Status:** 🟡 In Progress – transferability tables ingested; config wiring pending
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend rules/config
- **Description:** Model CRS skill-transferability combinations (education×language, foreign×Canadian work, certificate×language) as config-driven tables.
- **Dependencies:** CRS config schema, validation tests

#### [IRCC-203] Language CLB thresholds

- **Domain:** 3.5 Brain & AI
- **Status:** 🟡 In Progress – program minima captured; wiring to config/runtime pending
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend rules/config
- **Description:** Externalize CLB program minima for CEC/FSW/FST and per-ability CLB mappings for each accepted test in `config/domain/language.yaml`.
- **Dependencies:** Language test ingestion, config loader

#### [IRCC-204] NOC/TEER crosswalk

- **Domain:** 3.5 Brain & AI
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P1
- **Type:** Data/Integration
- **Description:** Design NOC 2021 code ↔ TEER crosswalk service with change monitoring; avoid copying full dataset—link to authoritative source.
- **Dependencies:** External NOC dataset/endpoint, caching

#### [IRCC-205] Biometrics & medical rules

- **Domain:** 3.5 Brain & AI
- **Status:** 🟡 In Progress – validity/reuse drafted; rule-engine wiring pending
- **Priority:** MEDIUM
- **Phase:** P1
- **Type:** Rules/config
- **Description:** Clarify medical exam validity, reuse rules, and biometrics deadlines; create “medical_required” checklist logic in domain knowledge/config.
- **Dependencies:** Domain knowledge updates, config schemas, workflow integration

#### [IRCC-206] Express Entry program rules (FSW/CEC/FST/PNP) – engine wiring

- **Domain:** 3.5 Brain & AI
- **Status:** 🔵 Planned
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Rules/config
- **Description:** Implement program eligibility evaluation (FSW/CEC/FST + EE-aligned PNP flag) using config-driven thresholds (language CLB, work TEER, education/ECA, funds) before CRS ranking.
- **Dependencies:** Program rules docs, CLB tables, work/education models, PoF rules

#### [IRCC-207] ADR engine & UI flows

- **Domain:** 3.5 Brain & AI
- **Status:** 🔵 Planned
- **Priority:** P2
- **Phase:** P1
- **Type:** Rules/config + UX
- **Description:** Model ADR categories/flags (work, funds, education, identity/police, medical/biometrics), tie to checklist templates, due dates, and applicant notifications.
- **Dependencies:** ADR overview, documents pipeline, workflow/task/notifications

#### [IRCC-208] PNP linkage rules (Express Entry)

- **Domain:** 3.5 Brain & AI
- **Status:** 🔵 Planned
- **Priority:** P2
- **Phase:** P1
- **Type:** Rules/config
- **Description:** Capture enhanced vs non-EE PNP handling, +600 CRS nomination application, and routing impacts on eligibility/checklists.
- **Dependencies:** CRS additional points, program family docs, province stream metadata

#### [IRCC-209] NOC/TEER eligibility resolver

- **Domain:** 3.5 Brain & AI
- **Status:** 🔵 Planned
- **Priority:** P1
- **Phase:** P1
- **Type:** Rules/config
- **Description:** Implement NOC 2021 → TEER lookup and EE eligibility flagging (skilled vs non-skilled), with change monitoring and external lookup support.
- **Dependencies:** NOC crosswalk docs, work experience model, config/external datasets

#### [IRCC-210] Arranged employment rules (EE)

- **Domain:** 3.5 Brain & AI
- **Status:** 🔵 Planned
- **Priority:** P1
- **Phase:** P1
- **Type:** Rules/config
- **Description:** Implement arranged-employment validation (TEER 0–3, LMIA/LMIA-exempt job offer, duration, non-seasonal, employer constraints) and expose to eligibility + CRS engines.
- **Dependencies:** Arranged employment docs, work experience model, employer/LMIA data

#### [ENG-RULE-001] Implement rule engine skeleton

- **Domain:** 3.5 Brain & AI
- **Status:** 🔵 Planned
- **Priority:** P1
- **Phase:** P1
- **Type:** Backend rules/config
- **Description:** Implement core rule engine that takes a normalized candidate profile and produces eligibility + CRS breakdown per program, using config/domain YAMLs and domain_knowledge as reference.
- **Dependencies:** RULE_ENGINE_OVERVIEW.md, RULE_ENGINE_CRS_ELIGIBILITY.md, config/domain schemas

#### [ENG-RULE-002] Wire config/domain to rule engine

- **Domain:** 3.5 Brain & AI
- **Status:** ✅ Done
- **Priority:** P1
- **Phase:** P1
- **Type:** Backend rules/config
- **Description:** Define YAML schemas for CRS and eligibility (e.g., crs.yaml, eligibility.yaml) and load/validate them in the rule engine.
- **Dependencies:** rule engine skeleton, schema design, domain_knowledge references
- **Notes:** Implemented via PR #19; see ENGINEERING_LOG entry dated 2025-12-09 `[rules][crs_engine][config_wiring_complete]`.

#### [ENG-RULE-004] Config admin UI/editor (follow-up)

- **Domain:** 3.5 Brain & AI
- **Status:** 🔵 Planned
- **Priority:** P3
- **Phase:** P2
- **Type:** Backend/Frontend tooling
- **Description:** Build a safe admin surface (or agent) to edit/validate config/domain/\*.yaml, including drafts, approvals, and rollout toggles.
- **Dependencies:** ENG-RULE-002 config models/loader, governance rules

#### [ENG-RULE-003] Golden test suite for CRS & eligibility

- **Domain:** 3.5 Brain & AI
- **Status:** 🔵 Planned
- **Priority:** P2
- **Phase:** P1
- **Type:** Testing
- **Description:** Add golden test cases for eligibility and CRS, including edge cases (continuity gaps, TEER 4/5 rejection, expiring tests/medicals/biometrics, funds exemptions), using domain_knowledge as oracle.
- **Dependencies:** rule engine skeleton, config wiring, test fixtures from domain_knowledge

#### [ENG-RULE-004] Program Eligibility Engine (FSW/CEC/FST)

- **Domain:** 3.5 Brain & AI
- **Status:** ✅ Done
- **Priority:** P1
- **Phase:** P1
- **Type:** Backend rules/config
- **Description:** Config-driven program eligibility evaluation for FSW, CEC, FST using ConfigService + RuleEngineService; returns structured reasons/warnings.
- **Dependencies:** config/domain/programs.yaml, language.yaml, work_experience.yaml, proof_of_funds.yaml

#### [ENG-RULE-005] Document & Forms Matrix

- **Domain:** 3.5 Brain & AI
- **Status:** ✅ Done
- **Priority:** P1
- **Phase:** P1
- **Type:** Backend rules/config
- **Description:** Config-driven forms/documents matrix (forms.yaml, documents.yaml) plus Case skeleton assembly via DocumentMatrixService and CaseService.
- **Dependencies:** ConfigService, DocumentMatrixService, RuleEngineService, config/domain/forms.yaml, config/domain/documents.yaml

#### [ENG-RULE-006] Case Evaluation API & Explainability

- **Domain:** 3.5 Brain & AI
- **Status:** ✅ Done
- **Priority:** P1
- **Phase:** P1
- **Type:** Backend API
- **Description:** Config-driven Case Evaluation API exposing program eligibility, CRS breakdown, and document/forms matrix with explainability metadata.
- **Dependencies:** RuleEngineService, DocumentMatrixService, CaseService, config/domain/*.yaml

#### [ENG-CASE-001] Case Lifecycle Engine (M4.1)

- **Domain:** 3.3 Cases & Workflows
- **Status:** 🟡 In Progress
- **Priority:** P1
- **Phase:** P1
- **Type:** Backend persistence + API
- **Description:** Tenant-aware case lifecycle with Tenant/User models, CaseRecord ownership/status, immutable snapshots and audit events, and lifecycle API for submit/review/complete/archive.
- **Dependencies:** CaseRecord/CaseSnapshot/CaseEvent, Tenant/User models, lifecycle service, branch protection + CI

#### [ENG-RULE-007] Case History & Audit (Phase 3.5)

- **Domain:** 3.5 Brain & AI
- **Status:** ✅ Done
- **Priority:** P1
- **Phase:** P1
- **Type:** Backend persistence + API
- **Description:** Persist evaluated cases with canonical CaseRecord, immutable CaseSnapshot versions, and CaseEvent audit entries; expose internal read-only APIs for listing and retrieving history.
- **Dependencies:** Case Evaluation API, ConfigService hashes, Alembic migrations, CaseHistoryService

#### [ENG-RULE-008] User/Tenant-Scoped Case History (Phase 4)

- **Domain:** 3.5 Brain & AI
- **Status:** 🔵 Planned
- **Priority:** P1
- **Phase:** P4 (Future)
- **Type:** Backend persistence + AuthN/AuthZ
- **Description:** Link case history to authenticated users/tenants, enforce scoping/RBAC, and secure history APIs for production use.
- **Dependencies:** ENG-RULE-007 data model, auth/tenant context propagation, audit logging

### 3.6 Agentic & Automation

#### [AA-001] Multi-Agent Runtime & Scheduler

- **Domain:** 3.6 Agentic & Automation
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P1
- **Type:** AI Orchestration
- **Description:** Stand up agent runtime (queues, sandboxes, guardrails) for Mastermind/Law/Workflow agents `[BP-09]`.
- **Source:** BP-09, BP-14 Gap #14
- **Dependencies:** Observability, audit logging, Config agent

#### [AA-002] Config Agent & Metadata Service

- **Domain:** 3.6 Agentic & Automation
- **Status:** 🔴 Missing
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend Service
- **Description:** Create natural-language-to-config service for forms, checklists, templates, and feature flags `[BP-09 §Config Agent]`.
- **Source:** BP-09, Master Spec §4.4
- **Dependencies:** Workflow service, schema registry, audit logging

#### [AA-003] End-User Automation UX

- **Domain:** 3.6 Agentic & Automation
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Frontend + AI UX
- **Description:** Surface agent suggestions, approvals, and automation toggles within consultant/client UIs `[BP-03 §5.4]`.
- **Source:** BP-03, PRD §4.1
- **Dependencies:** Workflow service, agent runtime

#### [AA-004] Task Auto-Generation & Assignment Hooks

- **Domain:** 3.6 Agentic & Automation
- **Status:** 🟡 Partial
- **Priority:** HIGH
- **Phase:** P1
- **Type:** Backend Service
- **Description:** Extend existing scaffolding so rules/agents automatically create, assign, and monitor tasks with ATDD coverage `[BP-08]`.
- **Source:** BP-08, WORKFLOW_TASK_TEST_PLAN.md
- **Dependencies:** Workflow service GA, Config agent

#### [AA-005] Agent Guardrails & Audit Toolkit

- **Domain:** 3.6 Agentic & Automation
- **Status:** 🟡 Partial
- **Priority:** MEDIUM
- **Phase:** P1
- **Type:** Infra / Compliance
- **Description:** Implement sandboxing, rate limits, human approval flows, and explainability dashboards `[BP-09 §Safety]`.
- **Source:** BP-09, BP-10
- **Dependencies:** Agent runtime, observability, audit logging

### 3.7 Reporting & Analytics

#### [RA-001] Operational Dashboards

- **Domain:** 3.7 Reporting & Analytics
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Backend + Frontend
- **Description:** Build dashboards for case throughput, workload, and SLA adherence `[BP-03]/[BP-13]`.
- **Source:** BP-03, BP-13, Gap #5
- **Dependencies:** Data warehouse, event ingestion

#### [RA-002] Predictive Analytics & Forecasting

- **Domain:** 3.7 Reporting & Analytics
- **Status:** 🔴 Missing
- **Priority:** LOW
- **Phase:** P3
- **Type:** AI/Analytics
- **Description:** Deliver predictive success rates, intake forecasts, and revenue projections `[BP-13 Phase 3]`.
- **Source:** BP-13, Gap #5
- **Dependencies:** Operational dashboards, AI runtime

#### [RA-003] Financial & Trust Reporting

- **Domain:** 3.7 Reporting & Analytics
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Backend + Reporting
- **Description:** Provide billing, trust reconciliation, and tax/AML-ready exports `[BP-03 §5.3]`.
- **Source:** BP-03, Gap #20
- **Dependencies:** Billing service, audit logging

#### [RA-004] Client Satisfaction & NPS Analytics

- **Domain:** 3.7 Reporting & Analytics
- **Status:** 🔴 Missing
- **Priority:** LOW
- **Phase:** P3
- **Type:** Frontend + Data
- **Description:** Collect feedback, sentiment, and NPS across journeys `[BP-03 §4.1]`.
- **Source:** BP-03, PRD §4
- **Dependencies:** Communication hub, analytics pipeline

#### [RA-005] Immigration KPI Benchmarking

- **Domain:** 3.7 Reporting & Analytics
- **Status:** 🔴 Missing
- **Priority:** LOW
- **Phase:** P3
- **Type:** Analytics / Data
- **Description:** Benchmark approval rates, timelines, and province-level metrics vs. industry `[BP-13]`.
- **Source:** BP-13, Gap #5
- **Dependencies:** Data warehouse, CRS/eligibility services

### 3.8 Expansion & Future Markets

#### [EX-001] Integration Marketplace & Developer Portal

- **Domain:** 3.8 Expansion / Future
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Platform
- **Description:** Ship public marketplace, webhook system, SDKs, and partner onboarding `[BP-13 §Integrations]`.
- **Source:** BP-13, Gap #7
- **Dependencies:** API standards, billing, authentication

#### [EX-002] Partnership & Ecosystem Program

- **Domain:** 3.8 Expansion / Future
- **Status:** 🔴 Missing
- **Priority:** LOW
- **Phase:** P2
- **Type:** Ops / BizTech
- **Description:** Build tooling + workflows for referral, reseller, and educational partners `[BP-13 §Partnerships]`.
- **Source:** BP-13, Gap #24
- **Dependencies:** CRM, billing, reporting

#### [EX-003] Multi-Language & Regional Expansion

- **Domain:** 3.8 Expansion / Future
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Platform + Frontend
- **Description:** Localize product for French-first Canada, then extend to new geographies (UK/AUS/US) `[BP-13 §Global Expansion]`.
- **Source:** BP-13, Gap #6
- **Dependencies:** Localization framework, compliance research

#### [EX-004] Native Mobile Apps (Consultant + Client)

- **Domain:** 3.8 Expansion / Future
- **Status:** 🔴 Missing
- **Priority:** MEDIUM
- **Phase:** P2
- **Type:** Mobile
- **Description:** Build iOS/Android apps with biometric auth, push notifications, and offline capture `[BP-13 §Mobile]`.
- **Source:** BP-13, Gap #4
- **Dependencies:** API stability, notification service, offline storage

#### [EX-005] International Tax & Financial Compliance Pack

- **Domain:** 3.8 Expansion / Future
- **Status:** 🔴 Missing
- **Priority:** LOW
- **Phase:** P3
- **Type:** Compliance / Backend
- **Description:** Extend billing/financial services to support multi-currency, tax reporting, and jurisdiction-specific rules `[BP-13 §Phase 3]`.
- **Source:** BP-13, Gap #20
- **Dependencies:** Financial reporting, localization, legal research

- [DONE] Observability baseline (M4.4): structured logging, request IDs, health/ready/metrics endpoints.
- [OPEN] Observability enhancements: tracing, Prometheus/Grafana integration, alerting/SLOs, per-tenant dashboards.
