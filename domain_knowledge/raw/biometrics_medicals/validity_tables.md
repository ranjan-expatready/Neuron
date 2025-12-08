# Biometrics & Medical Validity Tables (DRAFT)
> Values transcribed from IRCC pages as of 2025-12-08; SME/legal validation required before production use.

## table_name: biometrics_validity
source_url: https://www.cic.gc.ca/english/visit/biometrics.asp
columns: [age_min, age_max, program_type, validity_years, exemptions_notes, reuse_rules]
rows:
  - [14, 79, "Visitor / Study / Work / PR applicants", "N/A (status-driven)", "Exempt if outside 14–79 or program-specific exemption; check IRCC eligibility tool", "If prior biometrics for visitor/study/work/PR are still valid, reuse permitted; confirm via IRCC Check Status Tool"]
  - [0, 13, "All", "N/A", "Under 14 typically exempt unless otherwise specified", "Not applicable"]
  - [80, 120, "All", "N/A", "80+ typically exempt unless otherwise specified", "Not applicable"]

## table_name: medical_exam_validity
source_url: https://www.cic.gc.ca/english/information/medical/medexams-temp.asp; https://www.cic.gc.ca/english/information/medical/medexams-perm.asp
columns: [program_type, validity_months, reuse_rules, notes]
rows:
  - ["Temporary residence (visitor/study/work) with IME", 12, "Results reusable within 12 months of exam date; new exam needed if not used before expiry", "Letter of introduction shows expiry if applicable; panel physician exams only"]
  - ["Permanent residence", 12, "Results valid 12 months from exam; if landing after expiry, new IME required", "Landing must occur before exam expiry; panel physician required"]
