# Documents & Evidence – Overview (DRAFT, Engineering View)

## Purpose
Catalogs common documents/evidence required across programs and links them to case workflows.

## Key Entities / Fields
- Document type/category (identity, civil status, police certificate, medical, education, employment, funds).
- Issuer, issuance date, expiry/validity.
- File metadata: format, size limits, language/translation requirements.

## Relationships
- Tied to checklists/tasks in workflows.
- Some documents (police, medical) have validity windows and may be requested again (ADRs).

## Suggested Data Model (draft)
- `document_type { id, name, category, validity_days, translation_required_flag }`
- `document_requirement { program_family, stage, doc_type_id, mandatory_flag }`
- `uploaded_document { candidate_id, doc_type_id, issued_on, expires_on, language, verification_status }`

## Sources
- See `domain_knowledge/raw/documents/sources.md`

## Status
- DRAFT – requires SME/legal review before production.
