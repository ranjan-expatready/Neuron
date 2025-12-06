# Engineering Governance

## 1. Purpose & Scope
This document defines the FAANG-style governance loop for every agent (Cursor, GPT, automation scripts, humans) working on Neuron-2. Always read and follow these rules **before** writing code, tests, or docs so that persistent memory, product status, and blueprint intent stay aligned.

## 2. Agent Bootstrap Checklist
1. **Load runtime + knowledge paths:** Read `.ai-knowledge-base.json` (backend/frontend commands, CI behavior, blueprint links).
2. **Review product status:** Read `PRODUCT_LOG.md` to understand which features/sections are ✅, 🟡, 🧩, or ⛔.
3. **Review latest engineering changes:** Read the last few entries in `.ai-memory/ENGINEERING_LOG.md`.
4. **Skim relevant blueprint docs:**
   - Always: `blueprint/00_BLUEPRINT_INDEX.md`
   - Product/features: 01, 02, 03, 04, 13, 14
   - Architecture/infra/test strategy: 05, 06, 07, 08, 11
   - Operations/support: 12
   - AI/agents/automation: 09
5. **Confirm branch:** Use `main` for reading; create/checkout a dedicated feature branch (`feature/<name>`) before making changes.
6. **Confirm CI guardrails:** `backend-tests` (pytest + ≥80% coverage) and `frontend-tests` (lint + build) are required status checks on `main`. Local work should mirror those commands.

## 3. Change Types & Required Memory Updates

| Type | Definition | Required updates |
|------|------------|------------------|
| **Type A – Backend feature / bugfix** | Touches `backend/src/app/**`, `backend/tests/**`, schemas, services, or APIs. | - Add/adjust backend tests.<br>- Append ENGINEERING_LOG entry (include date, `[backend][area]` tags, summary, key files).<br>- Update PRODUCT_LOG section A/C if behavior or API is user-visible. |
| **Type B – Frontend feature / bugfix** | Touches `frontend/src/**`, Next.js routes, frontend tests, Playwright flows. | - Add/adjust frontend/unit/E2E tests.<br>- ENGINEERING_LOG entry with `[frontend]` tag.<br>- PRODUCT_LOG section B/C/E if UX changes (screens, flows, data shown). |
| **Type C – Infra / CI / DevOps** | Touches workflows, Makefiles, Docker, scripts, runtime automation. | - ENGINEERING_LOG entry with `[infra][ci]` tags.<br>- PRODUCT_LOG section F bullet describing the new guardrail/tooling. |
| **Type D – AI/Agent / Automation / CRS / Brain** | Touches AI agents, orchestration, CRS calculators, automation flows. | - ENGINEERING_LOG entry `[ai][automation]`.<br>- PRODUCT_LOG section D/E bullet describing capability & blueprints referenced.<br>- Reference blueprint/09, blueprint/13 as appropriate. |
| **Type E – Documentation-only** | Pure docs (blueprint updates, guides, runbooks) without code. | - ENGINEERING_LOG entry `[docs]` when material (new requirements, workflows, policies).<br>- PRODUCT_LOG only if doc introduces/retire user-facing functionality. |

**Example ENGINEERING_LOG entry (Type C):**
```
## 2025-12-05 – [ci][devops] CI guardrails live on main
- [branch-protection] Required `backend-tests` + `frontend-tests`, strict up-to-date, no force pushes.
- [ci] Renamed workflow jobs so each status has a unique context; reran pipelines (green).
- [docs] Updated PRODUCT_LOG section F to describe guardrails for future agents.
```

**Example PRODUCT_LOG bullet (Type B):**
```
- ✅ Client login UX hardened – `/auth/login` now uses JSON endpoint, adds inline validation, and redirects to `/dashboard` after success.
```

## 4. Engineering Log Format
* File: `.ai-memory/ENGINEERING_LOG.md`
* Heading format: `## YYYY-MM-DD – [tags] short summary`
* Use concise bullets (3–6 lines) covering:
  - Area (backend/frontend/infra/ai/docs).
  - Key modules or files.
  - Tests/CI impact or follow-up work.
* Always append (never rewrite history). List newest entry at the top.

## 5. Product Log Usage
* `PRODUCT_LOG.md` is the single source of truth for product readiness (sections A–F).
* Any change that affects user-visible behavior, roadmap status, or Go-To-Market messaging **must** update the relevant section.
* Before proposing or building new work, agents MUST read PRODUCT_LOG to avoid duplicating completed work or diverging from roadmap priorities.

## 6. Governance Loop Summary
1. **Before coding:** Run the Agent Bootstrap Checklist (Section 2).
2. **During implementation:** Keep each change scoped to one change type when possible; follow its required memory/product updates.
3. **Before pushing:** Run relevant tests (backend-tests, frontend-tests, e2e if touched). Update ENGINEERING_LOG (and PRODUCT_LOG if applicable).
4. **On PR:** Ensure `backend-tests` and `frontend-tests` are green, and reference the ENGINEERING_LOG entry (date + tags) in the PR description.
5. **After merge:** Confirm logs/KB are committed so future sessions can resume seamlessly.

## 7. Domain Knowledge Check (IRCC / Immigration)
- Applies to any CRS, eligibility, checklist, questionnaire, or workflow item tied to immigration rules.
- **Before implementation:**
  1. Locate the relevant backlog ID in `PRODUCT_BACKLOG.md` to confirm scope/dependencies.
  2. Review `domain_knowledge/` (raw + processed) for the supporting IRCC/PNP evidence.
  3. If evidence is missing or marked draft, use Octagon (or the approved research tool) to discover official sources and propose what to ingest.
  4. Ask the human owner to confirm priority documents and authorize storing them under `domain_knowledge/raw/`.
  5. Summarize into `domain_knowledge/processed/` with citations and validation status before writing code.
- Draft summaries are acceptable for development, but production-critical logic must be reviewed by an immigration SME.
- **Octagon may accelerate research and drafting, but `domain_knowledge/` remains the canonical store for immigration rules.**
