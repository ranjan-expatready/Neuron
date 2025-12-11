# Form Autofill & Submission Architecture (M10.1, docs-only)

> Purpose: Define the architecture, data model, agents, and governance for Neuron’s Form Autofill & IRCC Submission layer. This is a design-only milestone; **no runtime code changes** in M10.1. The spec must enable future engineers/agents to implement M10.2+ without ambiguity.

## 1) Problem Statement & Scope
- Automate assembly of IRCC application packages (PDF forms + web-style flows) from canonical profile, document matrix outputs, and rule engine results—while keeping RCIC firmly in control.
- In-scope for Phase 10:
  - Autofill IRCC PDFs/structured forms using config-driven mappings from canonical data/documents.
  - Produce human-reviewable “application packages” (forms + evidence checklist + warnings) for RCIC review.
  - Model IRCC web flows as structured “web-flow definitions” parallel to PDF forms (steps/fields).
- Out-of-scope for M10.1:
  - Actual PDF/HTML filling code.
  - Browser automation or direct IRCC submission.
  - Any AUTO mode; all outputs are drafts for RCIC review.

## 2) Conceptual Model
- **FormDefinition**: `{ id: "IMM0008", label, version, effective_date, fields[], metadata }`
  - Field attributes: `field_id`, `label`, `type`, `required`, `control`, `help`, `constraints`.
- **FormFieldMapping**: links canonical data_path → `form_field_id` (with optional transforms, e.g., formatting dates, enumerations).
- **FormBundle / ApplicationPackage**: set of FormDefinitions required for a program + checklist of supporting docs; includes ordering and per-form status.
- **WebFlowDefinition**: IRCC online flow modeled as steps/sections with fields (mirrors FormDefinition; enables future browser-automation adapter).
- **Relationships**:
  - Canonical profile feeds mappings.
  - Document matrix resolves required docs; forms reference doc ids for attachments/evidence.
  - Case lifecycle: package generation is gated to cases in “pre-submit” states; outputs become part of AgentActions and case history snapshots.

## 3) Config-First Design
- All definitions/mappings live in config (`config/domain/forms.yaml`, `config/domain/form_mappings.yaml` or equivalent). **No hard-coded IRCC field ids/labels in code.**
- Versioning:
  - Each FormDefinition carries `version`, `effective_from`, optional `supersedes`.
  - Mappings are versioned and statused: `draft | in_review | active | retired`.
  - Support coexistence of multiple IRCC form versions; “active” tagged per tenant/program.
- Safety:
  - RCIC review required before a mapping becomes active.
  - Drafts proposed by agents flow through the existing draft/approval pipeline (consistent with M7.x intake config lifecycle).

## 4) Agents & Roles
- **FormMappingAgent (shadow)**:
  - Inputs: form PDF metadata/version, canonical field dictionary, prior mappings, diff vs previous version.
  - Outputs: proposed FormFieldMappings in `draft` status, with rationale and unmapped fields list.
  - Mode: SHADOW only; writes to drafts, never activates.
- **FormAutofillAgent (shadow)**:
  - Inputs: `case_id`, program, plan, active mappings, canonical profile, document checklist, available documents.
  - Outputs: autofill preview (field→value + source path + confidence/reason + warnings), assembled per-form payloads, attachment suggestions.
  - Mode: SHADOW only; logs AgentActions; no file upload or submission.
- **SubmissionPrepAgent (shadow)**:
  - Inputs: autofill preview + document reviewer findings + rule engine outputs (eligibility/CRS).
  - Outputs: application package summary (forms, attachments, consistency checks, missing info), human-readable action list for RCIC.
  - Mode: SHADOW only; prepares tasks, no submissions.
- Integration:
  - All agents use `AgentSession`/`AgentAction` with `agent_name`, `mode=shadow`, `status=suggested`, `auto_mode=false`.
  - Orchestration aligns with NEURON_AGENTIC_ORCHESTRATION_ARCHITECTURE (manual/event triggers, tenant-scoped).

## 5) Data Flow & APIs (design only)
- Proposed endpoints (not implemented in M10.1):
  - `POST /api/v1/cases/{case_id}/forms/autofill-preview`: triggers FormAutofillAgent, returns per-form field/value pairs with `source`, `confidence/reason`, `warnings`.
  - `GET /api/v1/cases/{case_id}/forms/package`: fetch latest generated application package (forms + evidence list + warnings + status).
  - `GET /api/v1/forms/definitions`: list active FormDefinitions with versions.
  - `GET /api/v1/forms/mappings/{form_id}`: fetch active mapping + draft deltas.
- Response shape (preview):
  ```json
  {
    "case_id": "...",
    "program": "EE_FSW",
    "forms": [
      {
        "id": "IMM0008",
        "version": "2024-01",
        "fields": [
          {
            "field_id": "uci",
            "value": "1234-5678",
            "source": "profile.identifiers.uci",
            "confidence": "high|medium|low",
            "reason": "direct mapping",
            "warnings": []
          }
        ],
        "attachments": [
          {"doc_type": "passport_main", "document_id": "doc-123", "status": "present"}
        ],
        "form_warnings": ["missing spouse info", "multiple address histories — choose one"]
      }
    ]
  }
  ```
- Audit & history:
  - Each autofill run logs an AgentAction (payload includes mappings version, config hashes, warnings).
  - Case history snapshot may include a pointer to the package manifest (not files) for auditability.

## 6) Safety, Governance, Review
- No direct IRCC submissions; all outputs are drafts requiring RCIC approval.
- Logging: every agent run creates AgentAction with `auto_mode=false`, `mode="shadow"`, `status="suggested"`.
- Conflict handling: when multiple candidate sources exist, return alternatives + reasons; default to blank with warning, not guesses.
- Partial data: leave fields empty with structured `missing_reason` (e.g., “profile.family.spouse missing”).
- Testing strategy (future):
  - Unit: mapping resolution (canonical → form field) with fixtures per form version.
  - Integration: end-to-end autofill preview for synthetic cases (single, spouse, dependants).
  - Regression sets: curated synthetic case sets with expected packages; re-run on mapping changes.

## 7) Phasing Plan (M10.x / M11.x)
- **M10.1 (this doc)**: Architecture/spec only; no runtime code.
- **M10.2**: Config schema + loaders for FormDefinition and FormFieldMapping (YAML + DB drafts), status lifecycle aligned with intake/doc drafts; no runtime autofill.
- **M10.3**: Backend FormAutofillEngine service to resolve mappings into per-form payloads; returns JSON preview; still SHADOW-only; no PDF/web automation.
- **M10.4**: RCIC UI “Forms Preview” page to display packages, field values, sources, and warnings; download JSON manifest; no submission.
- **M11.x (future)**:
  - PDF fill/export adapters (config-driven field binding, renderer abstraction).
  - WebFlow automation adapters (Playwright/Selenium wrappers) behind strict flags, RCIC approval, and dry-run previews.
  - Submission orchestration with multi-agent review (Document Reviewer + FormAutofill + Eligibility) before any AUTO pathway is considered.
  - Advanced ML/LLM assists (optional, guarded) for unstructured field inference—always explainable and human-reviewed.

## 8) Mapping to Existing Architecture
- Reuses config-first principles from intake/document matrix; aligns with Agentic Orchestration doc (manual/event triggers, SHADOW mode).
- Uses canonical profile + document matrix outputs as primary sources; rule engine outputs (eligibility/CRS) provide consistency checks.
- AgentActions remain the audit trail; case history snapshots reference package manifests (not binary files) to avoid PII proliferation.

## 9) Future Considerations
- Tenant overrides: allow tenant-specific mapping variants and form version pinning.
- Localization: support bilingual labels/help, but internal mapping keys remain stable.
- Compliance: PII minimization in logs; redaction for manifests stored in history; encryption at rest for generated files (when implemented).
- Observability: metrics for autofill runs, warning rates, unmapped field counts, per-form completeness.

