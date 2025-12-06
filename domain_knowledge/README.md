# Domain Knowledge Hub

## Purpose
- Central store for Canadian immigration domain assets that power Neuron-2.
- Houses **official IRCC / PNP artifacts**: guides, program descriptions, CRS rules, fee tables, checklists, timelines, IMM forms (e.g., IMM 5257, IMM 0008), and provincial program docs.
- All Neuron-2 agents (backend, frontend, automation, AI) MUST consult this folder when implementing immigration-specific logic; Octagon/external tools are helpers, not production sources.

## Suggested Structure
```
domain_knowledge/
├── raw/         # Raw evidence: PDFs, HTML exports, downloaded text from IRCC/PNP sources.
├── processed/   # Curated Markdown/YAML/JSON summaries fit for application use.
└── index.md     # Human-readable index of what raw + processed materials exist (to be built incrementally).
```

## Trust Levels & Workflow
1. **Raw documents (`raw/`)** are immutable snapshots of official content. Always record source URL + fetched date.
2. **Processed summaries (`processed/`)** must:
   - Reference the specific raw file(s) used.
   - Declare status: `draft/unverified`, `partially verified`, or `reviewed/verified`.
   - Highlight open questions or assumptions before code depends on them.
3. Agents may treat `draft` summaries as *best-effort* guidance for development/testing, but **production-critical rules must be validated by a human immigration expert** before launching.

## Agent Rules
- Never invent immigration law, CRS scoring, or eligibility rules. If info is missing, mark it as such and escalate.
- Always link features / backlog items to concrete files inside `domain_knowledge/`.
- Use Octagon (or other research assistants) to discover/download materials, but **store them here first** before relying on them in code or docs.
- Keep change history clear: cite sources, note validation status, and document who transformed raw data into processed summaries.
