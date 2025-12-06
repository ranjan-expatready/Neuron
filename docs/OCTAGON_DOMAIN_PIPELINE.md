# Octagon-Assisted Domain Knowledge Pipeline

## 1. Overview
Octagon (and future research assistants) function as **discovery + ingestion agents**. They:
- Search IRCC, PNP, and provincial portals for up-to-date guidance, forms, and policy updates.
- Recommend which official documents to capture.
- Produce preliminary summaries that help populate `domain_knowledge/`.

Neuron-2 never treats Octagon’s output as legal truth. Instead, Octagon accelerates the process of building a vetted, version-controlled knowledge base inside the repository.

## 2. Pipeline Phases
### Phase 1 – Discovery
- Use Octagon to locate high-value sources: Express Entry guides, CRS rulebooks, IMM form lists, study/work/family program pages, provincial nomination hubs, fee schedules, etc.
- Capture metadata (URLs, publication dates, update cadence) for each candidate source.

### Phase 2 – Harvest
- Download or copy official material into `domain_knowledge/raw/` (PDFs, HTML dumps, text exports).
- Record provenance (source URL, fetched timestamp, any licensing considerations).
- Preserve files verbatim; no edits in `raw/`.

### Phase 3 – Structuring
- Convert raw evidence into structured summaries under `domain_knowledge/processed/`, e.g.:
  - `crs_rules.md`
  - `program_catalog.md`
  - `forms_index.md`
  - `pnp_rules.md`
- Every processed file must list:
  - The exact raw documents referenced.
  - Status flag: `draft`, `partially validated`, or `reviewed`.
  - Known gaps or questions requiring human/SME confirmation.

### Phase 4 – Implementation
- Product features (CRS calculators, eligibility flows, questionnaires, document checklists) READ from `domain_knowledge/processed/`, not directly from Octagon.
- Backlog items should cite both the processed file(s) and relevant raw sources so code reviewers can trace requirements.

## 3. Responsibilities & Boundaries
- **Octagon May:** discover sources, summarize content, highlight candidate documents, propose structures for processed files.
- **Octagon May NOT:** override official IRCC text, invent missing rules, or act as a production data source.
- **Repository = Canon:** once data lives in `domain_knowledge/`, it becomes the authoritative reference for Neuron-2. Unstored information must not be used in code.

## 4. Future Automation
- Plan scripted jobs to periodically re-run discovery, detect IRCC changes, and alert maintainers when raw documents need refreshing.
- Consider diff tooling that compares new downloads vs. existing raw files.
- Long term: integrate validation workflows so SMEs can mark processed summaries as “reviewed” before release.

For now, this document is the contract: Octagon accelerates research, but `domain_knowledge/` remains the single source of truth for immigration domain rules.
