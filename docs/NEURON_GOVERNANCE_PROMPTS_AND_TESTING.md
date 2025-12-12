# Neuron Governance, Prompts, and Testing

## 1) Governance Principles
- Clean main; feature branches only; branch protection with tests.
- Coverage targets: backend ≥85%; frontend tracked closely.
- Config-first: no IRCC magic numbers in code; use `config/domain/*.yaml`.
- Tenant-aware; RBAC enforced everywhere.
- No untracked junk; docs for every module/major feature; golden tags for stable milestones.

## 2) Canonical ChatGPT → Cursor Prompt Template (Standard Engineering Task)
- **ROLE**: ChatGPT acts as CTO/Architect/PM/Domain SME/QA/Security/Agent Designer; Cursor implements.
- **ALWAYS DO THIS FIRST**:
  - Read NEURON_* docs, ENGINEERING_GOVERNANCE, ROADMAP_AND_PHASES, .ai-knowledge-base.json, ENGINEERING_LOG, PRODUCT_LOG, PRODUCT_BACKLOG.
  - Run `git status -sb`; confirm single-agent Cursor mode and clean tree (except .cursor/).
- **TASK DESCRIPTION**: Clear milestone/feature/fix scope.
- **CONSTRAINTS**: Config-first; tenant/RBAC; no IRCC magic numbers; backwards compatibility as required.
- **DELIVERABLES**: Code/tests/docs; updates to ENGINEERING_LOG/PRODUCT_LOG/BACKLOG/KB; update NEURON_* docs if architecture/agent behavior changes.
- **GIT HYGIENE**: Feature branch naming, PR details, high-level change summary.

## 3) When to Update Which Anchor File
- NEURON_VISION_AND_ACTOR_SYSTEM: actor model/personas/journeys changes.
- NEURON_TECHNICAL_ARCHITECTURE: new major components or layering changes.
- NEURON_AGENTIC_PLATFORM_AND_AGENTS: new/updated agents, modes, workflows.
- NEURON_MEMORY_AND_KNOWLEDGE_MODEL: memory layers or resync protocol changes.
- NEURON_GOVERNANCE_PROMPTS_AND_TESTING: governance, prompting, or testing strategy updates.
- ROADMAP_AND_PHASES: phase/milestone status changes.
- `.ai-knowledge-base.json`: current milestone, test stats, high-level state.
- ENGINEERING_LOG: every meaningful engineering task/milestone.
- PRODUCT_LOG: product-visible features.
- PRODUCT_BACKLOG: new tasks/milestones discovered or completed.

## 4) Testing & E2E Strategy (High-level)
- Backend unit/integration tests; frontend component/page tests.
- Planned: synthetic persona scenarios; agent eval harness (shadow vs auto); Playwright/Cypress E2E for core flows.

