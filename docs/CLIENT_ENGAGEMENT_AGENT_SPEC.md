# Client Engagement Agent – Hybrid Mode Spec (M8.1, Design Only)

> Scope: Architecture/specification only. No runtime behavior changes, no LLM calls, no messaging sends in this milestone.

## 1) Overview & Goals
- Purpose: Provide RCICs a supervised agent (`client_engagement`) that drafts client communications and, when explicitly allowed, auto-sends low-risk reminders. Target outcomes: reduce manual follow-ups; improve client responsiveness; maintain auditability and safety.
- Relation to M8.0 Agentic Platform: builds on `AgentSession`/`AgentAction`, AgentOrchestrator, admin visibility. Uses Neuron core (cases, intake/document checklist, billing/CRS) as data sources; remains read-only for now.
- Hybrid stance: SHADOW (suggest-only) + AUTO (optional, limited). Human-in-the-loop and compliance are non-negotiable.

## 2) Roles & Modes
- Agent name: `client_engagement`.
- SHADOW MODE:
  - Generates suggested messages only.
  - Requires RCIC/admin review, edit, approve/reject before send.
  - No direct client delivery.
- AUTO MODE:
  - Allowed only for pre-approved, low-risk templates (e.g., “Please complete intake”, “We received your document”).
  - Tenant-configurable per event type and per channel; defaults to OFF.
  - Fully logged; can be disabled tenant-wide or per-case.
- Tenant/RCIC controls:
  - Enable/disable agent.
  - Toggle AUTO per event category/channel.
  - Restrict AUTO to specific templates; everything else remains SHADOW.

## 3) Event Model (Triggers)
Each event carries `{event_type, case_id, tenant_id, user_id?, occurred_at, context}`.

- Intake lifecycle: `intake_invited_no_start`, `intake_incomplete`, `intake_stale`.
- Document lifecycle: `docs_missing`, `doc_uploaded`.
- Case/evaluation: `crs_evaluated`, `eligibility_status_change`, `case_status_change`.
- Client comms: `client_message_received`, `client_question_received`.
- Admin/RCIC prompt: `rcic_request_reply`, `rcic_request_reminder`.

Eligibility per event:
- Shadow: all events.
- Auto: limited to low-risk (e.g., `intake_incomplete`, `docs_missing`, `doc_uploaded`, benign status acks), gated by tenant config.

## 4) Channels & Delivery
- Initial channels: in-app client portal notifications; email (via messaging service, not agent).
- Future: WhatsApp/SMS (design placeholder only).
- Message structure: `{channel, subject?, body, links?, locale, branding}`. Agent produces suggestion payload; Messaging Service owns send/retry/failed status. Failures feed back into `AgentAction` with `status=error`.

## 5) Safety, Compliance & Guardrails
- Must NOT: promise visa outcomes, suggest rule-breaking, change case data, submit to IRCC, bypass RBAC, or contradict RCIC guidance.
- Guardrails:
  - Risk keyword/intent flags → mark `requires_approval`; never auto-send.
  - Escalation path: tag action as `escalated` / `requires_rcic_review`.
  - Config flags: shadow-only mode, per-event AUTO allowlist, max frequency per client, locale/branding enforcement.

## 6) Memory Architecture (Agent-Specific)
- Case memory: session/action log of reminders, last contact time, questions answered; stored via `AgentSession`/`AgentAction`. Avoid excess PII; store minimal message metadata and template IDs.
- Agent memory: reusable templates/phrasing; response effectiveness stats (aggregated, non-PII).
- Global/domain memory: domain_knowledge, IRCC references, config/domain YAML. Engineering governance artifacts (`.ai-knowledge-base.json`, `.ai-memory/ENGINEERING_LOG.md`) are excluded from runtime memory.

## 7) Data Model & Contracts (proposed)
- Event → Orchestrator:
  - `{event_type, case_id, tenant_id, user_id?, occurred_at, context:{intake_progress?, missing_docs?, client_message_id?, risk_level?}}`
- Agent → Orchestrator (suggestion):
  - `{agent_name, action_type, status="suggested", case_id, tenant_id, payload:{message_type, channel, subject?, body, target_user_id?, template_id?, risk_level, requires_approval, suggested_mode: "shadow"|"auto"}}`
- Orchestrator → Messaging Service (future send):
  - `{case_id, tenant_id, channel, subject?, body, target_user_contact, branding, locale, correlation_ids:{session_id, action_id}}`

## 8) Hybrid Mode Workflows (descriptive)
- Workflow 1: Intake incomplete → Shadow Reminder
  1. Event `intake_incomplete`.
  2. Agent drafts reminder (shadow). Action logged `suggested`.
  3. RCIC reviews/edits in admin UI, clicks Send → messaging service sends; Action logged `executed`, RCIC decision captured.
- Workflow 2: Missing Documents → Auto Reminder
  1. Event `docs_missing`, tenant has AUTO enabled for doc reminders/email+in-app.
  2. Agent drafts approved template; orchestrator marks `suggested` + `executed`.
  3. Messaging service sends; send result logged (success/error) in action.
- Workflow 3: Client Question → Shadow Reply
  1. Event `client_question_received`.
  2. Agent drafts reply (requires_approval=true).
  3. RCIC edits/approves; messaging service sends; lifecycle logged (suggested → executed/rejected).

## 9) Configuration & Tenant Controls
- Settings (future storage via admin config UI/backing store):
  - Enable agent (on/off).
  - AUTO allowlist per event type and per channel.
  - Frequency caps (per day/week).
  - Language/tone, branding fields (RCIC name, firm).
  - Escalation defaults for high-risk content.

## 10) Observability, Audit & Dashboard
- Visibility:
  - `/admin/agents` and per-case “Agent Activity” tab show sessions/actions with filters.
  - Metrics: suggestions count, auto-sends, escalations, errors, response rates.
  - Logs: structured with tenant_id, case_id, agent_name, action_type, status, request_id.

## 11) Phases & Milestones
- M8.1: Spec only; no behavior changes.
- M8.2: Admin-triggered, template-based shadow suggestions (intake incomplete, missing docs, client questions); RCIC review UI; no LLM, no auto-send.
- M8.3: LLM-based draft replies (shadow-only, guardrails, template fallback) for client questions and optional reminder rewrites; still no auto-send.
- M8.4: AUTO mode rollout for low-risk reminders with tenant controls; messaging integration.
- M8.5+: Additional channels (WhatsApp/SMS), analytics, deeper orchestration with other agents.

