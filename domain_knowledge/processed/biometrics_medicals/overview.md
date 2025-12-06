# Biometrics & Medical Exams – Overview (DRAFT, Engineering View)

## Purpose
Outline biometric and medical exam requirements, validity, and how they fit into case workflows.

## Key Entities / Fields
- Biometrics: required flag, collection date, validity period, location/VAC.
- Medicals: panel physician exam date, category (PR/worker/student), validity period, results status.
- Exemptions or reuse eligibility (where applicable).

## Relationships
- Often triggered after submission; linked to tasks/notifications and ADRs.
- Program-specific applicability; some temporary streams differ from PR flows.

## Suggested Data Model (draft)
- `biometrics_record { candidate_id, required_flag, collected_on, expires_on, vac_location }`
- `medical_exam { candidate_id, exam_date, category, expires_on, status, panel_physician_id }`
- `workflow_trigger { stage, trigger_type, requirements }` for biometrics/medical requests.

## Sources
- See `domain_knowledge/raw/biometrics_medicals/sources.md`

## Status
- DRAFT – requires SME/legal review before production.
