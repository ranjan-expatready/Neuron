# Neuron Immigration OS — Vision & Actor System

## 1. Product Vision
- **Neuron Immigration OS** is a multi-tenant, agentic, config-first SaaS platform for regulated immigration professionals (e.g., Canadian RCICs and law firms).
- Goal: reach $1M+ ARR with an enterprise-grade OS for intake, eligibility/CRS, document management, agentic client engagement, and IRCC-aligned workflows.

### Core Principles
1) **Config-first** — Rules/CRS tables/documents/forms/intake live in `config/domain/*.yaml` + `domain_knowledge`; no IRCC magic numbers in code.
2) **Explainability-first** — Every decision (CRS, eligibility, checklist, lifecycle, agent suggestion) must be explainable to RCIC/client/auditor.
3) **Tenant-first** — All data and agent behavior are tenant-aware; RBAC and billing respect tenant boundaries.
4) **Human-in-the-loop** — Agents assist but do not replace regulated professionals; high-risk/regulatory decisions require approval.
5) **FAANG-grade engineering** — Tests, observability, branch protection, golden tags, documented architecture, and explicit governance.

## 2. Logical Actor System

### 2.1 Platform Owner / Product Team
- **Platform Owner (You)** — founder, product direction, risk appetite.
- **Neuron Product Engineering Team** — ChatGPT (CTO/Architect/PM/QA/Security/Agent Designer) + Cursor (Principal Engineer implementing code/tests/migrations/PRs).

### 2.2 Tenant Organization Actors
- **Tenant Admin** — manages users, roles, plan/billing, and tenant-scoped config.
- **RCIC / Consultant / Case Owner** — owns cases end-to-end; intake, docs, evaluation, engagement.
- **Case Worker / Assistant** — supports RCIC with data entry/follow-ups.
- **Compliance / Audit Role** — reviews case history, lifecycle events, agent actions, and logs.

### 2.3 Client (End Applicant)
- Provides personal data and documents via self-serve portal.
- Receives reminders/drafts via RCIC-managed channels; access is limited to their own case(s).

### 2.4 Product Admin Team (Platform Side)
- **Product Admin** — manages global configs (fields/templates/documents/forms), feature flags, agent capabilities, plan definitions; uses admin consoles for config/agents/observability.
- **Legal / Risk Approver** — approves major config or agent behavior changes (AUTO modes, new channels, IRCC mappings).

### 2.5 External System: IRCC
- Treated as external authority; Neuron aligns program definitions, forms, and workflows. Future: PDF autofill, browser co-pilot, IRCC API if/when available.

## 3. High-level User Journeys (Actor View)
- **Tenant Onboarding**: Platform Admin sets defaults → Tenant Admin signs up, selects plan, invites RCICs.
- **Case Lifecycle (RCIC-centric)**: Create case → Intake (RCIC or client self-serve) → Document checklist → CRS & eligibility → lifecycle transitions → submission-ready → archive.
- **Client Self-Serve**: Invite → login → fill intake → upload documents → receive reminders/guidance (RCIC/agent supervised).
- **Config & Governance**: Product Admin/Tenant Admin use admin consoles + draft/activation workflows to evolve intake/documents/forms.
- **Agentic Operations**: Agents propose actions (shadow) → RCIC/admin approves; AUTO used only for low-risk actions within guardrails.

