# Neuron Agentic Platform & Agents

## Agent Platform Core
- Persistence: `AgentSession` and `AgentAction` scoped by tenant/case/agent_name/status/payload/timestamps; `auto_mode` marks AUTO actions.
- Orchestrator: records sessions/actions; no cron/scheduler by default.

## Agent Inventory
- **Client Engagement Agent (M8.x)**: intake/missing-doc reminders, client question drafts; SHADOW (template/LLM) and limited AUTO for low-risk reminders.
- **Document Reviewer Agent (M9.1–M9.3, shadow)**: uses document matrix + case documents; M9.2 adds optional OCR/PDF-aware content extraction (DocumentContentService); M9.3 adds deterministic heuristics over OCR text/metadata (missing keywords, misplaced hints, expiry/quality signals, simple profile consistency); outputs required_present/required_missing/optional/duplicates/unmatched + warnings/heuristics; SHADOW-only; RCIC/admin review.
- **Document Reviewer Agent (future)**: deeper OCR/classification + ML/LLM quality checks, checklist mapping with issues.
- **Form Autofill & Submission Prep (future)**: config-driven PDF/IRCC export artifacts for human review.
- **Eligibility & Strategy Agent (future)**: explains eligibility/strategy using CRS/eligibility engines; human-reviewed.
- **Config & Rules Drafting Agent (future)**: proposes config drafts; never auto-activates.
- **Case Lifecycle Coach (future)**: suggests next-best actions from lifecycle state/history/documents/agent logs.

## Modes & Guardrails
- SHADOW: suggestions only; human approval required.
- HYBRID (future): safe internal adjustments only; no external comms without approval.
- AUTO: low-risk, template-based, tenant-configured; must log `auto_mode=true`.
- All agents: config-first (no hard-coded IRCC rules), tenant/case scoped, RBAC enforced, audit/observability required.

