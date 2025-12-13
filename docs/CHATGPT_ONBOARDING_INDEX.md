# ChatGPT Onboarding Index

## A) What This File Is (and Why It Exists)
This is the single-file, handoff-ready guide for resuming work across new ChatGPT sessions and Cursor worktrees without governance drift. It encodes how to re-establish state, verify alignment, and coordinate ChatGPT ↔ Cursor actions deterministically.
It does **not** replace the authoritative roadmap, logs, or knowledge base (see anchors below). Those remain the source of truth and must be read/updated per milestone.

## B) Canonical Governance Anchors (Authoritative Files)
- `docs/NEURON_GOVERNANCE_PROMPTS_AND_TESTING.md` – governance, prompting, testing strategy.
- `docs/NEURON_MEMORY_AND_KNOWLEDGE_MODEL.md` – memory layers and knowledge syncing.
- `docs/NEURON_TECHNICAL_ARCHITECTURE.md` – layered architecture and services.
- `docs/NEURON_VISION_AND_ACTOR_SYSTEM.md` – vision, actors, journeys.
- `docs/NEURON_AGENTIC_PLATFORM_AND_AGENTS.md` – agent inventory and behaviors.
- `docs/NEURON_AGENTIC_ORCHESTRATION_ARCHITECTURE.md` – orchestration model and guardrails.
- `docs/ROADMAP_AND_PHASES.md` – phases, milestones, and current position.
- `PRODUCT_LOG.md` – product-visible changes and releases.
- `PRODUCT_BACKLOG.md` – canonical backlog items and statuses.
- `.ai-memory/ENGINEERING_LOG.md` – engineering changes, tests, branches.
- `.ai-knowledge-base.json` – current phase/milestone/integration branch/golden tags/testing commands.

## C) Priority Rules (Resolve Conflicts)
Precedence (highest first):
1) Git branch + HEAD commit (actual checked-out state)
2) `.ai-knowledge-base.json` (current_phase/current_milestone/integration_branch/latest_golden_tag)
3) `docs/ROADMAP_AND_PHASES.md`
4) `PRODUCT_LOG.md` + `.ai-memory/ENGINEERING_LOG.md`
5) `PRODUCT_BACKLOG.md`
If any conflict exists, STOP and reconcile by updating the relevant docs/KB via a governance realignment PR—do not guess.

## D) Current Snapshot (Must Stay Updated Each Milestone PR)
- Current phase: Phase 12 – Submission Preparation (closed)
- Current milestone: P12.2 – Submission Preparation Review UI (completed, read-only/shadow)
- Integration branch: integration/phase10_forms_autofill
- Latest golden tag: v0.12.2-phase12-submission-prep-ui
- Integration HEAD commit: 33364a374e323b3abb1c0b6ad819efa8c6b3acad
- Last updated: 2025-12-13
Rule: This snapshot is refreshed in every milestone PR alongside roadmap/log/KB updates.

## E) Mandatory State Verification Checklist (Every Session, Before Work)
1) `git status -sb` (must be clean or intentionally dirty within the feature branch)
2) Confirm branch name (no detached HEAD for feature work)
3) Record `git rev-parse HEAD`
4) Confirm integration branch head: `git rev-parse origin/integration/phase10_forms_autofill` (or current integration branch)
5) Read `.ai-knowledge-base.json` keys: current_phase, current_milestone, integration_branch, latest_golden tag
6) Confirm `docs/ROADMAP_AND_PHASES.md` matches KB (phase/milestone)
7) Confirm `PRODUCT_LOG.md` and `.ai-memory/ENGINEERING_LOG.md` reflect current milestone
8) Confirm `PRODUCT_BACKLOG.md` status lines up with current milestone
9) Confirm branch protection expectations: approvals=1, required check context=`all`
Hard STOP: If any mismatch/conflict is found, do not proceed with feature work—open a governance realignment PR first.

## F) Branch / Worktree / CI Rules
- `integration/*` is PR-only; no direct pushes.
- If a worktree is locked, create a new tracking branch with a suffix (e.g., `_owt`) instead of fighting locks.
- Detached HEAD allowed only for tagging; never for feature work; must be documented in ENGINEERING_LOG.
- Required CI check context is `all`; ensure it runs on integration PRs.
- Approvals required: 1. Any temporary relaxations must be logged under governance exceptions.

## G) ChatGPT ↔ Cursor Operating Contract
- ChatGPT: Plans, runs governance checks, decides scope, manages risks, and instructs Cursor. Ensures state verification before work and demands governance updates after.
- Cursor: Executes commands/edits/tests, prepares PRs, and reports changes. Must summarize what changed and which governance files were updated.
- Human: Provides prompts, approves merges, performs minimal manual actions (e.g., GitHub merges).
- Sync rule: Cursor must always summarize code/docs changes and explicitly list updated governance files.

## H) Mandatory Prompt Templates (Copy/Paste)

### 1) NEW CHATGPT SESSION INIT TEMPLATE
```
You are ChatGPT resuming work. Read docs/CHATGPT_ONBOARDING_INDEX.md. Run state verification:
- git status -sb
- git rev-parse HEAD
- git rev-parse origin/integration/phase10_forms_autofill
- Read .ai-knowledge-base.json keys (phase/milestone/integration_branch/latest_golden_tag)
- Cross-check ROADMAP vs KB, PRODUCT_LOG, ENGINEERING_LOG, PRODUCT_BACKLOG
- Confirm branch protection (approvals=1, required check=all)
If any mismatch, STOP and propose a governance realignment PR. Otherwise, restate current phase/milestone and propose the next action, then produce a Cursor prompt.
```

### 2) NEW CURSOR AGENT INIT TEMPLATE
```
Read docs/CHATGPT_ONBOARDING_INDEX.md and governance anchors. Run state verification:
- git status -sb
- git rev-parse HEAD
- git rev-parse origin/integration/phase10_forms_autofill
- Read .ai-knowledge-base.json keys
- Cross-check ROADMAP/PRODUCT_LOG/ENGINEERING_LOG/BACKLOG for consistency
If any mismatch, STOP and report; do not code. Otherwise, proceed with the assigned task following governance and safety rules.
```

### 3) MILESTONE EXECUTION PROMPT TEMPLATE (MOST IMPORTANT)
```
Before coding:
- Run state verification (git status, HEAD, integration HEAD, KB keys, ROADMAP/LOG/ENGINEERING_LOG/BACKLOG alignment, branch protection).
- If mismatch, STOP and request a governance realignment PR.

Execution (shadow/safe as applicable):
- Implement scope.
- Run tests (backend/ frontend as applicable).

Post-work (mandatory governance updates):
- Update: docs/ROADMAP_AND_PHASES.md, PRODUCT_LOG.md, PRODUCT_BACKLOG.md, .ai-memory/ENGINEERING_LOG.md, .ai-knowledge-base.json, docs/CHATGPT_ONBOARDING_INDEX.md snapshot block.
- Summarize changes and tests.
- Prepare PR to integration branch with CI/all required.

Stop on any failure; report only the failure summary and await instruction.
```

## I) Update Discipline (Non-Negotiable Rule)
Every milestone PR MUST update:
- `docs/ROADMAP_AND_PHASES.md`
- `PRODUCT_LOG.md`
- `PRODUCT_BACKLOG.md`
- `.ai-memory/ENGINEERING_LOG.md`
- `.ai-knowledge-base.json`
- `docs/CHATGPT_ONBOARDING_INDEX.md`  ← required
If a milestone does not change phase/milestone/tag, still update this file’s snapshot block with a “no change required” note and refreshed `last_updated`. Keep this index concise; detailed history lives in logs.

## J) Anti-Patterns We Must Avoid (Lessons Learned)
- Letting agents run for hours without checkpoints.
- Assuming phase/milestone without checking KB + ROADMAP.
- Worktree branch locks causing stalled work (use new tracking branches instead).
- CI not triggering on integration PRs.
- Changing rulesets without recording an exception log.

---
### How to Use This File in 60 Seconds
1) New ChatGPT chat: paste the NEW CHATGPT SESSION INIT TEMPLATE, run state verification, confirm phase/milestone, and plan next steps.
2) New Cursor agent: paste the NEW CURSOR AGENT INIT TEMPLATE, run verification, STOP on mismatch.
3) Running a milestone: use the MILESTONE EXECUTION PROMPT TEMPLATE; after work, run tests and update all governance files plus this onboarding index snapshot; open PR to integration with CI/all required. Stop if any check fails.***

