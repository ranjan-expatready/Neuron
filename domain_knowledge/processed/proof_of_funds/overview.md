# Proof of Funds – Overview (DRAFT, Engineering View)

## Purpose
Defines how financial sufficiency is assessed for certain immigration programs (e.g., FSW/Express Entry) and how amounts vary by family size.

## Key Entities / Fields
- Family size, required amount (CAD), effective date of table, source reference.
- Acceptable instruments (balances, bank letters, investments) vs. exclusions (borrowed funds).
- Exemptions (e.g., valid job offer/LMIA, CEC).

## Relationships
- Tied to Express Entry eligibility (not CRS points directly).
- Family composition data and job-offer status influence applicability.

## Suggested Data Model (draft)
- `proof_of_funds_table { id, effective_date, family_size, required_amount_cad }`
- `proof_of_funds_rule { id, applies_to_program, exemption_conditions }`
- `proof_of_funds_evidence { candidate_id, doc_type, issued_on, balance_cad, institution }`

## Sources
- See `domain_knowledge/raw/proof_of_funds/sources.md`

## Status
- DRAFT – requires SME/legal review before production.
