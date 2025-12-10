# Agentic Platform & Client Engagement Agent (M8.0 Skeleton)

## 1. High-Level Architecture
- **Agentic Platform layer** sits alongside existing Neuron services (case lifecycle, intake engine, document matrix, billing, CRS, admin config/drafts).
- Core components:
  - **Agent Orchestrator**: opens agent sessions, records actions, enforces tenant/case scoping, and emits audit-grade logs.
  - **Agent Registry**: conceptual catalog of available agents (future work).
  - **Shared Memory & Logs**: session/action storage, tied to tenant + case where applicable.
  - **Tools/Integrations**: Neuron APIs (cases, intake, documents, config), future OCR/PDF parsers, vector memory, notifications.
- Relationship to existing systems:
  - Case lifecycle: agents operate per case/tenant; no automatic state changes in M8.0.
  - Intake/document engines: agents may read schemas/checklists; overrides remain YAML + active drafts.
  - Billing/CRS: informational only; no writeback.
  - Admin config/drafts: unchanged; agent actions are separately logged.

## 2. Agent Taxonomy (conceptual roles)
For each agent: responsibilities, inputs, outputs, safety.

- **Config Intake Proposer Agent**
  - Inputs: intake schemas, field drafts, domain knowledge.
  - Outputs: draft config proposals.
  - Safety: never activates configs; proposals only.
- **Rules & Eligibility Proposer Agent (future)**
  - Inputs: rule configs, CRS/eligibility outputs.
  - Outputs: draft rule adjustments.
  - Safety: no direct rule activation.
- **Document Ingestion & Reviewer Agent**
  - Inputs: uploaded docs, OCR/parsing outputs.
  - Outputs: quality flags, missing items, suggestions.
  - Safety: no auto-approvals; no PII leaks.
- **Document Autofill & Form Assembly Agent**
  - Inputs: canonical profile, form mappings.
  - Outputs: draft autofill payloads.
  - Safety: never submits to IRCC; human approval required.
- **Case Narrative & Recommendation Agent**
  - Inputs: case facts, eligibility/CRS.
  - Outputs: draft narratives/next steps.
  - Safety: no legal commitments; include disclaimers.
- **RCIC Workflow Copilot**
  - Inputs: tasks, deadlines, billing state.
  - Outputs: reminders/next actions.
  - Safety: no automatic lifecycle changes or billing adjustments.
- **Governance & QA Agent**
  - Inputs: config changes, agent actions.
  - Outputs: QA findings, audit notes.
  - Safety: read-only, advisory only.
- **Client Engagement Agent (primary for M8.x)**
  - Inputs: case intake status, checklist/missing docs, client questions.
  - Outputs: suggested reminders/explanations; LLM-assisted draft replies (shadow-only).
  - Safety: suggestions only; no sends, no commitments; RCIC override required; template fallback if LLM unavailable.
  - AUTO mode (M8.4): limited to intake/doc reminders, tenant-configurable, admin-triggered runner; logs executed actions with `auto_mode=true`; no auto LLM replies.

## 3. Memory & Persistence Model (product-level)
- **Case-scoped memory**:
  - `agent_sessions` per case/tenant.
  - `agent_actions` for audit-grade tracking (which agent, what action, payload, status).
  - Optional future `agent_messages`.
- **Agent-scoped memory**:
  - Reusable patterns and prompts (non-PII).
- **Global/domain memory**:
  - IRCC docs, `domain_knowledge/`, `config/domain/*.yaml`.
- Governance note: `.ai-knowledge-base.json` and `.ai-memory/ENGINEERING_LOG.md` are for engineering governance, not runtime agent memory.

## 4. Tools & Integrations (future-proofed; not implemented in M8.0)
- Neuron APIs: cases, profiles, intake schemas, document checklist, admin config/drafts, billing, CRS.
- OCR/PDF services: abstract via `DocumentParsingService` tool (stub).
- Vector memory: pgvector or external vector DB (future).
- Notifications/Email/SMS: not wired in M8.0; future integration points only.

## 5. Client Engagement Agent Spec (M8.0–M8.3)
- **Triggers (manual/admin)**: intake not started/incomplete, missing documents, client portal questions.
- **Actions**:
  - M8.0: deterministic placeholders.
  - M8.2: template-based reminders and question drafts, admin-triggered; logs `suggested`.
  - M8.3: LLM-assisted draft replies (shadow-only) with template fallback; optional LLM rewrite of reminder body text without changing required sections/docs.
  - M8.4: AUTO mode for intake/doc reminders only, tenant-controlled toggles + throttling, executed via admin-triggered runner; logged as `executed` with `auto_mode=true`.
- **Safety constraints**:
  - No direct IRCC interactions.
  - No legal commitments; include advisory phrasing.
  - RCIC/admin override before any send/execute path.
  - If LLM fails or disabled, fallback to template draft; log whether LLM was used.
- **Current scope (M8.4)**: shadow + AUTO for intake/doc reminders (admin-triggered), audit-logged; client questions remain shadow-only. No cron, no auto LLM sends.

