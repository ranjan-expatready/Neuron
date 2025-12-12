# Neuron Memory & Knowledge Model

## 1) Memory Layers
- **Data-level**: DB tables (cases, snapshots/events, documents, agent sessions/actions, billing, tasks).
- **Config-level**: `config/domain/*.yaml` (fields, templates, options, documents, forms, rules); drafts + activation tables override baseline when ACTIVE.
- **Product/Engineering memory**: `.ai-knowledge-base.json`, `.ai-memory/ENGINEERING_LOG.md`, `PRODUCT_LOG.md`, `PRODUCT_BACKLOG.md`, `docs/ROADMAP_AND_PHASES.md`.
- **Architecture memory**: NEURON_* docs (vision/actor, technical architecture, agents, memory model, governance/prompts/testing).

## 2) ChatGPT Resync Protocol (New Chat)
1. User provides: NEURON_* docs, ENGINEERING_GOVERNANCE, ROADMAP_AND_PHASES, .ai-knowledge-base.json, last 20–30 lines of ENGINEERING_LOG, PRODUCT_LOG, PRODUCT_BACKLOG, current golden tag + active branch.
2. ChatGPT reads them, reconstructs: current phase/milestone, architecture invariants, agent capabilities/constraints, recent changes, pending backlog.
3. ChatGPT emits the task prompt for Cursor aligned to constraints, with mandatory governance steps.

## 3) Agent Memory & Learning (Future)
- Learn from `AgentAction` patterns (false positives/negatives), adjust prompts/heuristics with evals.
- Use non-PII aggregates; preserve explainability.

