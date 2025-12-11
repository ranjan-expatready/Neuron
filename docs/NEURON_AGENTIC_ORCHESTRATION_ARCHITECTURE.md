# Neuron Agentic Orchestration Architecture (M8.6)

## 1. Purpose & Scope
- Defines how Neuron’s agents are orchestrated across tenants, cases, and channels, including trigger types (manual, event-based, future time-based), mode gating (SHADOW/HYBRID/AUTO), RBAC/tenant isolation, safety guardrails, memory usage, and tool integrations (LLM, OCR/PDF, IRCC co-pilot).
- Architecture-only: no runtime code changes in M8.6. Builds on Phase 8 work (M8.0–M8.4) and existing NEURON_* docs.
- Current foundation in place: AgentSession/AgentAction (M8.0); Client Engagement Agent with SHADOW/LLM and limited AUTO for safe reminders (M8.1–M8.4).

## 2. Agent Inventory & Responsibilities
- **Client Engagement Agent (implemented)**: intake incomplete reminders; missing docs reminders; client question replies. Modes: SHADOW (template/LLM), limited AUTO (safe, tenant-controlled). Channels: today draft/UI; future email/in-app.
- **Document Reviewer Agent (future)**: OCR + document matrix to classify docs, detect missing/inconsistent evidence; outputs structured findings; SHADOW first.
- **Form Autofill & Submission Prep Agent (future)**: uses canonical profile + mappings to fill PDFs and prepare IRCC portal checklists; outputs artifacts for human review.
- **Eligibility & Strategy Agent (future)**: uses CRS + program eligibility + profile to explain eligibility and suggest strategy; always human-reviewed.
- **Config & Rules Drafting Agent (future)**: proposes changes to fields/templates/documents/forms; feeds intake config draft/activation pipeline; never directly activates.
- **Case Lifecycle Coach Agent (future)**: reads lifecycle state, history, documents, CRS/eligibility, agent log; suggests next steps/tasks for RCIC/team.
- **Global principles for all agents**: config-first (rules from config/domain + domain_knowledge), tenant/case scoped, human-in-the-loop for high-risk decisions, observability/audit-first.

## 3. Orchestration Model
### 3.1 Trigger Types
- **Manual**: RCIC/admin “Generate suggestions” on a case; tenant admin runs scoped auto flows.
- **Event-based**: case state changes (intake progress, docs updated, ready-to-submit), new document upload, profile changes (IELTS, job offer), billing nearing limit.
- **Time-based (future, tenant-flagged)**: sweeps for overdue intake/docs or approaching deadlines with rate limits and opt-in controls.

### 3.2 Orchestration Decisions
- For each trigger: choose agent(s), order, mode (SHADOW/HYBRID/AUTO), and context (case, tenant, profile, docs, CRS, prior AgentActions).
- Examples:
  - Single-agent: intake incomplete → Client Engagement Agent → reminder draft.
  - Sequential: new docs → Document Reviewer Agent → if gaps → Client Engagement Agent draft reminder.
  - Combined: major eligibility change → Eligibility Agent explanation → Case Lifecycle Coach suggestion → Engagement Agent draft message.
- All steps logged in AgentSession/AgentAction; deterministic structure even if content uses LLM.

### 3.3 Mode Gating (SHADOW / HYBRID / AUTO)
- **SHADOW**: suggestions only; status="suggested"; requires human UI approval.
- **HYBRID (future)**: may auto-adjust internal metadata/tasks; no external comms or legal-impactful changes without approval.
- **AUTO**: only low-risk, template-based ops; tenant feature flags, per-agent/channel settings, rate/min-days caps; log `auto_mode=true`. M8.4 already enables limited AUTO for engagement reminders; future AUTO must conform to this architecture and RBAC/tenant guardrails.

## 4. Permissions, RBAC, and Safety
- **Tenant isolation**: orchestrator/agents operate within a single tenant context; no cross-tenant access.
- **RBAC**: admin/owner/RCIC can trigger flows, configure settings, enable/disable AUTO; case-level triggers require case access.
- **Guardrails**: agents do not directly modify configs, legal decisions, or core case statuses without human confirmation; no billing bypass.
- **LLM safety**: all LLM calls via LLMClient (env-configured); safe system prompts; no IRCC rules hard-coded; `llm_used` metadata logged.
- **Data minimization**: agents receive only data required for the task; no indiscriminate full-case dumps.

## 5. Agent Memory & Context
- Inputs: canonical profile; case history (CaseSnapshot/CaseEvent); document matrix/state; AgentAction history; billing state; config/domain YAML; intake config drafts/overrides.
- Outputs: AgentAction records as the auditable memory of proposals/actions per case; recomputable suggestions over structured state rather than long conversational logs.

## 6. Tools & Integrations (Design Only)
- **LLM**: already used by Client Engagement Agent (shadow replies); future use for document review explanations, eligibility explanations, RCIC-friendly summaries.
- **OCR/PDF**: to be wrapped as OCRService, PDFFormService, DocumentParsingService; agents call service interfaces (not libraries directly).
- **IRCC Co-pilot (future)**: structured exports for IRCC portals and optional browser automation driven by auditable plans; human supervision required.

## 7. Observability & Dashboards for Agentic Flows
- Metrics: per-agent action counts, error rates, AUTO vs SHADOW ratios, per-tenant stats.
- Logs: structured with request_id, session_id, agent_name, tenant_id, case_id, mode, status.
- UI: `/admin/agents` remains primary view for sessions/actions; future per-tenant agent dashboards.

## 8. Roadmap Mapping (M9+)
- M9.x: Document Reviewer Agent (shadow-only) using this orchestration model.
- M10.x: Form Autofill Engine (PDF + IRCC export).
- M11.x: Eligibility & Strategy Agent.
- M12.x: Case Workflow Coach/Automation.
- M13.x: IRCC co-pilot and deeper AUTO within guardrails.
- This doc is the canonical reference; update it whenever new agents/orchestration behaviors are added. All M9+ implementation PRs must reference and conform to it.

