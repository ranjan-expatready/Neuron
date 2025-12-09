# CRS Skill Transferability & Additional Points (RAW) — DRAFT, NOT LEGAL ADVICE
source_url: https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score/crs-criteria.html  
date_accessed: 2025-12-08  
note: Values copied from IRCC CRS criteria page. All numbers require SME/legal validation before production use.

## Foreign Work Experience (summary bundles)
table_name: crs_transfer_foreign_summary  
columns: [factor, condition, points]  
rows:
  - [foreign_work + strong_language, "CLB 7+ plus foreign work experience", 50]
  - [foreign_work + canadian_work, "Foreign work experience plus Canadian work experience", 50]

## Certificate of Qualification (summary bundle)
table_name: crs_transfer_certificate_summary  
columns: [factor, condition, points]  
rows:
  - [certificate_of_qualification + strong_language, "Certificate of qualification with good/strong official language proficiency", 50]

## Education + Language
table_name: crs_transfer_education_language  
columns: [education_level, clb_band, points]  
rows:
  - [high_school_or_less, "CLB7+ (one or more under 9)", 0]
  - [high_school_or_less, "CLB9+ (all four)", 0]
  - [postsec_1yr_plus, "CLB7+ (one or more under 9)", 13]
  - [postsec_1yr_plus, "CLB9+ (all four)", 25]
  - [two_or_more_creds_one_3yr_plus, "CLB7+ (one or more under 9)", 25]
  - [two_or_more_creds_one_3yr_plus, "CLB9+ (all four)", 50]
  - [masters_or_entry_to_practice, "CLB7+ (one or more under 9)", 25]
  - [masters_or_entry_to_practice, "CLB9+ (all four)", 50]
  - [doctorate, "CLB7+ (one or more under 9)", 25]
  - [doctorate, "CLB9+ (all four)", 50]
notes: CLB7+ rows correspond to “points for CLB 7 or more… one or more under CLB 9”; CLB9+ rows correspond to “CLB 9 or more on all four abilities”.

## Education + Canadian Work Experience
table_name: crs_transfer_education_canadian_work  
columns: [education_level, canadian_work, points]  
rows:
  - [high_school_or_less, "1 year", 0]
  - [high_school_or_less, "2+ years", 0]
  - [postsec_1yr_plus, "1 year", 13]
  - [postsec_1yr_plus, "2+ years", 25]
  - [two_or_more_creds_one_3yr_plus, "1 year", 25]
  - [two_or_more_creds_one_3yr_plus, "2+ years", 50]
  - [masters_or_entry_to_practice, "1 year", 25]
  - [masters_or_entry_to_practice, "2+ years", 50]
notes: Points buckets align to IRCC “education + 1 year Cdn work” and “education + 2+ years Cdn work”.

## Foreign Work Experience + Language
table_name: crs_transfer_foreign_language  
columns: [foreign_work, clb_band, points]  
rows:
  - [none, "CLB7+ (one or more under 9)", 0]
  - [none, "CLB9+ (all four)", 0]
  - ["1-2 years", "CLB7+ (one or more under 9)", 13]
  - ["1-2 years", "CLB9+ (all four)", 25]
  - ["3+ years", "CLB7+ (one or more under 9)", 25]
  - ["3+ years", "CLB9+ (all four)", 50]

## Foreign Work Experience + Canadian Work
table_name: crs_transfer_foreign_canadian_work  
columns: [foreign_work, canadian_work, points]  
rows:
  - [none, "1 year", 0]
  - [none, "2+ years", 0]
  - ["1-2 years", "1 year", 13]
  - ["1-2 years", "2+ years", 25]
  - ["3+ years", "1 year", 25]
  - ["3+ years", "2+ years", 50]

## Certificate of Qualification + Language
table_name: crs_transfer_certificate_language  
columns: [certificate_status, clb_band, points]  
rows:
  - [certificate_present, "CLB5+ (one or more under 7)", 25]
  - [certificate_present, "CLB7+ (all four)", 50]

## Additional Points (summary caps)
table_name: crs_additional_points_summary  
columns: [factor, max_points]  
rows:
  - [sibling_in_canada, 15]
  - [french_language, 50]
  - [canadian_post_secondary, 30]
  - [provincial_nomination, 600]

## Additional Points (breakdown)
table_name: crs_additional_points_breakdown  
columns: [factor, condition, points]  
rows:
  - [sibling, "Sibling in Canada (18+, PR/citizen)", 15]
  - [french, "NCLC 7+ all four; CLB ≤4 English or no English test", 25]
  - [french, "NCLC 7+ all four; CLB 5+ all four English", 50]
  - [canadian_study, "Post-secondary credential 1–2 years in Canada", 15]
  - [canadian_study, "Post-secondary credential 3+ years in Canada", 30]
  - [provincial_nomination, "Provincial/territorial nomination", 600]
notes: Job-offer points are absent on this page (per Mar 25, 2025 removal noted elsewhere). All values DRAFT pending SME validation.

