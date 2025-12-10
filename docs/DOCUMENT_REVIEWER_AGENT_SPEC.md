# Document Reviewer Agent & Document Intelligence Pipeline (M9.0 Spec)

> Scope: Design/spec only. No runtime code changes, no external integrations implemented in this milestone.

## 1) Overview & Goals
- Purpose: Assist RCICs by reviewing uploaded documents (passports, PoF, work letters, etc.), surfacing issues, and mapping uploads to the checklist.
- Outcomes: Faster validation, fewer missing/incorrect docs, fully auditable recommendations via `AgentSession`/`AgentAction`.
- Relationships:
  - Intake/document matrix/checklist (`config/domain/documents.yaml`, intake engine).
  - Case history for audit trails.
  - Client portal uploads and RCIC/admin uploads.
  - Agentic platform (sessions/actions, orchestrator, admin visibility).

## 2) Document Ingestion & Lifecycle
- Flow: Upload (client/RCIC) → storage (object path/db ref per current service) → classification → checklist association → reviewer decision.
- Storage: Reuse existing document model/service; no new storage semantics defined here.
- Mapping: Uploaded docs link to checklist entries via document codes in `documents.yaml`.
- States (conceptual): `uploaded` → `classified` → `pending_review` → `accepted | rejected` → `superseded`.
- Supersession: New upload for same requirement marks prior as superseded (not auto-deleted).

## 3) OCR & Text Extraction Abstraction
- Define `DocumentTextExtractor` interface:
  - `extract_text(document_ref)` → raw text + metadata.
  - `extract_structured(document_ref)` (optional) → key-value hints.
- M9.0: Spec only; no provider wiring.
- Future providers: cloud OCR/vision, on-prem, or Tesseract. All must be behind this abstraction.
- Privacy/residency: configurable provider; avoid sending PII outside allowed region; redaction hooks for logs.

## 4) Document Understanding & Classification
- Signals: filename, mimetype, upload slot/context, OCR patterns (e.g., MRZ for passport, “statement” for bank docs).
- `DocumentClassifier` concept:
  - Input: document_ref, extracted text, upload context.
  - Output: `document_type_code`, confidence, evidence/snippets.
- Supports rule-based first, ML/LLM later; provider-agnostic contract.

## 5) Checklist Integration
- Use `documents.yaml` + intake/document matrix to know required/optional docs per program/plan and conditions.
- Agent maps uploads to requirements:
  - Suggest “This upload satisfies requirement X” or “Does not match any required doc; possible matches: …”.
- Uses existing checklist resolution (IntakeEngine/document matrix) to identify missing items.

## 6) Quality Checks & Risk Flags
- Checks (examples):
  - Expiry detection (passports/visas).
  - Date range for bank statements/pay stubs.
  - Page count vs expectation; low resolution; unreadable OCR ratio.
  - Language mismatch (non-English/French if required).
- Emit `DocumentIssue` objects: `{code, severity(info|warn|blocker), explanation, suggested_action}`.

## 7) Document Reviewer Agent Behavior
- Agent name: `document_reviewer`.
- Modes:
  - Shadow (M9.x initial): never auto-accept/reject. Proposes classification, checklist mapping, issues, and recommendations; RCIC confirms/overrides.
  - Future auto mode (later): only for high-confidence, low-risk docs.
- Actions logged to `AgentAction`:
  - `classification_suggestion`, `quality_issue_detection`, `checklist_mapping_suggestion`, `review_recommendation`.
  - Payload includes document_id, suggested document_type_code, confidence, issues, checklist target, and risk flags.

## 8) Memory & Auditability
- Per-case memory: documents reviewed, issues raised/ignored, agent recommendations vs RCIC decisions, timestamps.
- Agent memory (future): false positive/negative patterns, template prompts; non-PII aggregates only.
- Audit: every recommendation as `AgentAction` tied to `document_id` and tenant/case; no mutation of original files.

## 9) Tooling & Model Choices (Future-Friendly)
- Abstractions: `DocumentTextExtractor`, `DocumentClassifier`, `DocumentIssueDetector`.
- Potential tools:
  - OCR: cloud vision, on-prem OCR, open-source.
  - Classification: rules → ML/LLM classifiers.
  - Text QA/flagging: LLM with strict prompts (no legal guarantees, no hallucinated requirements).
- Swappable providers without changing agent API; config-driven selection.

## 10) Admin & RCIC UX
- Admin:
  - Configure which doc types are auto-classified, thresholds for “high confidence”.
  - View overrides and audit trails.
- RCIC (case-level “Documents & Review” tab):
  - See uploads, checklist matches, agent suggestions.
  - Approve/reject classification, mark issues valid/ignored.
  - History showing agent vs RCIC decisions.

## 11) Safety, Compliance & Limits
- Must NOT auto-delete files, change case state, or mark “ready to submit” without RCIC approval.
- Must NOT send data to external OCR/LLM without explicit config.
- Must avoid hallucinating requirements; rely on config/domain knowledge.
- Keep logs/audit with tenant isolation; redact sensitive text in logs.

## 12) Phased Roadmap (M9.x)
- M9.0 (this spec): Design only.
- M9.1: Implement agent scaffold + basic classification from metadata/context (no OCR).
- M9.2: Add OCR abstraction + pluggable provider.
- M9.3: Quality checks + issues UI.
- M9.4+: ML/LLM-based doc understanding; auto mode for low-risk docs; analytics.

