# Neuron Agentic Platform & Agents

## 1) Agentic Platform Core
- Persistence: `AgentSession` and `AgentAction` tables scoped by tenant/case/agent_name/action_type/status/payload/timestamps.
- Sessions group related actions; actions capture suggestions/executions with audit payloads; `auto_mode` flag differentiates AUTO vs shadow.

## 2) Agent Types & Roles
- **Client Engagement Agent**:
  - Scenarios: intake incomplete reminders, missing docs reminders, client question replies (shadow).
  - Modes: template, LLM-assisted (shadow), AUTO for low-risk reminders (intake/docs).
- **Document Reviewer Agent (future)**:
  - Uses OCR and document matrix; suggests classification, issues, checklist mapping; shadow first.
- **Rule/Config Assistant (future)**:
  - Proposes config drafts for intake/templates/documents/forms.
- **Case Lifecycle Agent (future)**:
  - Suggests lifecycle transitions/next steps under guardrails.
- Others (future): eligibility explainer, analytics/insights.

## 3) Agent Modes
- **SHADOW**: Logs suggestions only; human approval required.
- **HYBRID**: Pre-executes safe subsets; still requires approval.
- **AUTO**: Executes low-risk actions under tenant-configured guardrails; fully logged.

## 4) Safety & Guardrails
- Agents must not modify legal decisions/config without proper workflows.
- No unsupervised client sends outside approved channels/templates.
- All actions logged to `AgentAction`; admin UI visibility; RBAC + tenant isolation enforced.

## 5) Agent Observability
- Metrics: actions per agent, errors, escalations, AUTO vs shadow ratio.
- Logs: structured, tenant/case-scoped.
- Admin UI: `/admin/agents` for sessions/actions, filters; per-case views for engagement.

