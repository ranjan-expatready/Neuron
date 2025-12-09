# CRS Scoring and Eligibility Rules

## Document Purpose

This document provides detailed information about the Comprehensive Ranking System (CRS) scoring methodology and eligibility rules for Canadian immigration programs. This information is intended for system development and AI agent training purposes.

**⚠️ DISCLAIMER: This document is for product development purposes only and does not constitute legal advice. CRS scoring rules and eligibility criteria change frequently. Always consult current IRCC resources and qualified immigration professionals for legal guidance.**

---

## Comprehensive Ranking System (CRS) Overview

### CRS Structure
The CRS is a points-based system used to rank Express Entry candidates. The maximum possible score is 1,200 points, distributed across four main categories:

```yaml
crs_structure:
  core_factors: "Maximum 600 points"
  skill_transferability: "Maximum 100 points"
  additional_points: "Maximum 600 points"
  total_maximum: "1,200 points"
```

---

## Core Factors (Maximum 600 Points)

### With Spouse or Common-Law Partner

#### Age (Maximum 100 Points)
```yaml
age_points_with_spouse:
  "17 or under": 0
  "18": 90
  "19": 95
  "20-29": 100
  "30": 95
  "31": 90
  "32": 85
  "33": 80
  "34": 75
  "35": 70
  "36": 65
  "37": 60
  "38": 55
  "39": 50
  "40": 45
  "41": 35
  "42": 25
  "43": 15
  "44": 5
  "45 or over": 0
```

#### Education (Maximum 140 Points)
```yaml
education_points_with_spouse:
  "Less than secondary school": 0
  "Secondary diploma (high school graduation)": 28
  "One-year program at university, college, trade or technical school, or other institute": 84
  "Two-year program at university, college, trade or technical school, or other institute": 91
  "Bachelor's degree OR three or more year program at university, college, trade or technical school, or other institute": 112
  "Two or more certificates, diplomas, or degrees. One must be for a program of three or more years": 119
  "Master's degree, OR professional degree needed to practice in a licensed profession": 126
  "Doctoral level university degree (PhD)": 140
```

#### Official Language Proficiency (Maximum 150 Points)
```yaml
first_language_points_with_spouse:
  speaking:
    "CLB 4-5": 0
    "CLB 6": 8
    "CLB 7": 16
    "CLB 8": 22
    "CLB 9": 29
    "CLB 10+": 34
  
  listening:
    "CLB 4-5": 0
    "CLB 6": 8
    "CLB 7": 16
    "CLB 8": 22
    "CLB 9": 29
    "CLB 10+": 34
  
  reading:
    "CLB 4-5": 0
    "CLB 6": 8
    "CLB 7": 16
    "CLB 8": 22
    "CLB 9": 29
    "CLB 10+": 34
  
  writing:
    "CLB 4-5": 0
    "CLB 6": 8
    "CLB 7": 16
    "CLB 8": 22
    "CLB 9": 29
    "CLB 10+": 34

second_language_points:
  all_abilities_clb_5_or_higher: 22
  all_abilities_clb_4_or_lower: 0
```

#### Canadian Work Experience (Maximum 70 Points)
```yaml
canadian_work_experience_with_spouse:
  "None or less than 1 year": 0
  "1 year": 35
  "2 years": 46
  "3 years": 56
  "4 years": 63
  "5 or more years": 70
```

### Without Spouse or Common-Law Partner

#### Age (Maximum 110 Points)
```yaml
age_points_without_spouse:
  "17 or under": 0
  "18": 99
  "19": 105
  "20-29": 110
  "30": 105
  "31": 99
  "32": 94
  "33": 88
  "34": 83
  "35": 77
  "36": 72
  "37": 66
  "38": 61
  "39": 55
  "40": 50
  "41": 39
  "42": 28
  "43": 17
  "44": 6
  "45 or over": 0
```

#### Education (Maximum 150 Points)
```yaml
education_points_without_spouse:
  "Less than secondary school": 0
  "Secondary diploma (high school graduation)": 30
  "One-year program at university, college, trade or technical school, or other institute": 90
  "Two-year program at university, college, trade or technical school, or other institute": 98
  "Bachelor's degree OR three or more year program at university, college, trade or technical school, or other institute": 120
  "Two or more certificates, diplomas, or degrees. One must be for a program of three or more years": 128
  "Master's degree, OR professional degree needed to practice in a licensed profession": 135
  "Doctoral level university degree (PhD)": 150
```

#### Official Language Proficiency (Maximum 160 Points)
```yaml
first_language_points_without_spouse:
  speaking:
    "CLB 4-5": 0
    "CLB 6": 9
    "CLB 7": 17
    "CLB 8": 23
    "CLB 9": 31
    "CLB 10+": 37
  
  listening:
    "CLB 4-5": 0
    "CLB 6": 9
    "CLB 7": 17
    "CLB 8": 23
    "CLB 9": 31
    "CLB 10+": 37
  
  reading:
    "CLB 4-5": 0
    "CLB 6": 9
    "CLB 7": 17
    "CLB 8": 23
    "CLB 9": 31
    "CLB 10+": 37
  
  writing:
    "CLB 4-5": 0
    "CLB 6": 9
    "CLB 7": 17
    "CLB 8": 23
    "CLB 9": 31
    "CLB 10+": 37

second_language_points_without_spouse:
  all_abilities_clb_5_or_higher: 24
  all_abilities_clb_4_or_lower: 0
```

#### Canadian Work Experience (Maximum 80 Points)
```yaml
canadian_work_experience_without_spouse:
  "None or less than 1 year": 0
  "1 year": 40
  "2 years": 53
  "3 years": 64
  "4 years": 72
  "5 or more years": 80
```

### Spouse or Common-Law Partner Factors (Maximum 40 Points)

#### Spouse Education (Maximum 10 Points)
```yaml
spouse_education_points:
  "Less than secondary school": 0
  "Secondary diploma (high school graduation)": 2
  "One-year program at university, college, trade or technical school, or other institute": 6
  "Two-year program at university, college, trade or technical school, or other institute": 7
  "Bachelor's degree OR three or more year program": 8
  "Two or more certificates, diplomas, or degrees": 9
  "Master's degree, OR professional degree": 10
  "Doctoral level university degree (PhD)": 10
```

#### Spouse Language Ability (Maximum 20 Points)
```yaml
spouse_language_points:
  "CLB 4 or less in all abilities": 0
  "CLB 5 or more in all four abilities": 20
```

#### Spouse Canadian Work Experience (Maximum 10 Points)
```yaml
spouse_canadian_work_experience:
  "None or less than 1 year": 0
  "1 year": 5
  "2 years": 7
  "3 years": 8
  "4 years": 9
  "5 or more years": 10
```

---

## Skill Transferability Factors (Maximum 100 Points)

### Education + Language Proficiency
```yaml
education_language_transferability:
  conditions:
    education: "Post-secondary degree"
    language: "CLB 7 or higher in all first language abilities"
  
  points:
    "Secondary school or less": 0
    "Post-secondary degree + CLB 7": 13
    "Post-secondary degree + CLB 9+": 25
    "Two or more post-secondary degrees + CLB 7": 25
    "Two or more post-secondary degrees + CLB 9+": 50
```

### Education + Canadian Work Experience
```yaml
education_canadian_work_transferability:
  conditions:
    education: "Post-secondary degree"
    work_experience: "1+ years Canadian work experience"
  
  points:
    "Post-secondary degree + 1 year Canadian experience": 13
    "Post-secondary degree + 2+ years Canadian experience": 25
    "Two or more post-secondary degrees + 1 year Canadian experience": 25
    "Two or more post-secondary degrees + 2+ years Canadian experience": 50
```

### Foreign Work Experience + Language Proficiency
```yaml
foreign_work_language_transferability:
  conditions:
    work_experience: "1+ years foreign work experience"
    language: "CLB 7 or higher in all first language abilities"
  
  points:
    "1 year foreign experience + CLB 7": 13
    "1 year foreign experience + CLB 9+": 25
    "2+ years foreign experience + CLB 7": 25
    "2+ years foreign experience + CLB 9+": 50
```

### Foreign Work Experience + Canadian Work Experience
```yaml
foreign_canadian_work_transferability:
  conditions:
    foreign_experience: "1+ years foreign work experience"
    canadian_experience: "1+ years Canadian work experience"
  
  points:
    "1 year foreign + 1 year Canadian": 13
    "1 year foreign + 2+ years Canadian": 25
    "2+ years foreign + 1 year Canadian": 25
    "2+ years foreign + 2+ years Canadian": 50
```

### Certificate of Qualification + Language Proficiency
```yaml
certificate_language_transferability:
  conditions:
    certificate: "Certificate of qualification in skilled trade"
    language: "CLB 5 or higher in all first language abilities"
  
  points:
    "Certificate + CLB 5": 25
    "Certificate + CLB 7+": 50
```

---

## Additional Points (Maximum 600 Points)

### Provincial Nomination
```yaml
provincial_nomination:
  points: 600
  note: "Virtually guarantees invitation to apply"
```

### Job Offer
```yaml
job_offer_points:
  noc_teer_00:
    description: "Senior management occupations"
    points: 200
  
  noc_teer_0_1_2_3:
    description: "Other NOC TEER 0, 1, 2, or 3 occupations"
    points: 50
  
  requirements:
    - "Written job offer"
    - "Full-time for at least 1 year"
    - "Non-seasonal"
    - "From employer with positive LMIA or LMIA-exempt"
```

### Canadian Education
```yaml
canadian_education_points:
  "1 or 2-year post-secondary program": 15
  "3+ year post-secondary program": 30
  "Two or more post-secondary programs (one 3+ years)": 30
  
  requirements:
    - "Completed at designated learning institution"
    - "Studied full-time for at least 8 months"
    - "Physically present in Canada for at least half the program"
```

### Sibling in Canada
```yaml
sibling_points:
  points: 15
  requirements:
    - "Brother or sister who is Canadian citizen or permanent resident"
    - "18 years of age or older"
    - "Living in Canada"
```

### French Language Proficiency
```yaml
french_language_points:
  strong_french_weak_english:
    description: "CLB 7+ in all French abilities, CLB 4 or less in English"
    points: 25
  
  strong_french_good_english:
    description: "CLB 7+ in all French abilities, CLB 5+ in all English abilities"
    points: 30
```

---

## Federal Skilled Worker (FSW) Points System

### FSW Selection Factors (Separate from CRS)
```yaml
fsw_selection_factors:
  education:
    maximum: 25
    "University PhD": 25
    "University Master's or professional degree": 23
    "Two or more university degrees at bachelor's level": 22
    "University degree of three years or more": 21
    "University degree of two years": 19
    "University degree of one year": 15
    "Two-year college diploma": 13
    "One-year college diploma": 12
    "High school diploma": 5
  
  language:
    maximum: 28
    first_official_language:
      "High proficiency (CLB 9+)": 24
      "Moderate proficiency (CLB 7-8)": 16
      "Basic proficiency (CLB 5-6)": 8
      "No proficiency (CLB 4 or less)": 0
    second_official_language:
      "High proficiency (CLB 9+)": 4
      "Moderate proficiency (CLB 7-8)": 4
      "Basic proficiency (CLB 5-6)": 4
      "No proficiency (CLB 4 or less)": 0
  
  work_experience:
    maximum: 15
    "6+ years": 15
    "4-5 years": 13
    "2-3 years": 11
    "1 year": 9
    "Less than 1 year": 0
  
  age:
    maximum: 12
    "18-35": 12
    "36": 11
    "37": 10
    "38": 9
    "39": 8
    "40": 7
    "41": 6
    "42": 5
    "43": 4
    "44": 3
    "45": 2
    "46": 1
    "47+": 0
  
  arranged_employment:
    maximum: 10
    "Valid job offer": 10
    "No job offer": 0
  
  adaptability:
    maximum: 10
    factors:
      "Spouse's education": "3-5 points"
      "Previous study in Canada": "5 points"
      "Previous work in Canada": "10 points"
      "Arranged employment": "5 points"
      "Relatives in Canada": "5 points"

minimum_pass_mark: 67
```

---

## Language Test Equivalencies

### Canadian Language Benchmarks (CLB) to Test Scores

#### IELTS General Training
```yaml
ielts_clb_equivalency:
  speaking:
    "CLB 10": "7.5"
    "CLB 9": "7.0"
    "CLB 8": "6.5"
    "CLB 7": "6.0"
    "CLB 6": "5.5"
    "CLB 5": "5.0"
    "CLB 4": "4.0"
  
  listening:
    "CLB 10": "8.5"
    "CLB 9": "8.0"
    "CLB 8": "7.5"
    "CLB 7": "6.0"
    "CLB 6": "5.5"
    "CLB 5": "5.0"
    "CLB 4": "4.5"
  
  reading:
    "CLB 10": "8.0"
    "CLB 9": "7.0"
    "CLB 8": "6.5"
    "CLB 7": "6.0"
    "CLB 6": "5.0"
    "CLB 5": "4.0"
    "CLB 4": "3.5"
  
  writing:
    "CLB 10": "7.5"
    "CLB 9": "7.0"
    "CLB 8": "6.5"
    "CLB 7": "6.0"
    "CLB 6": "5.5"
    "CLB 5": "5.0"
    "CLB 4": "4.0"
```

#### CELPIP General
```yaml
celpip_clb_equivalency:
  all_abilities:
    "CLB 10": "10"
    "CLB 9": "9"
    "CLB 8": "8"
    "CLB 7": "7"
    "CLB 6": "6"
    "CLB 5": "5"
    "CLB 4": "4"
```

#### TEF Canada (French)
```yaml
tef_clb_equivalency:
  speaking:
    "CLB 10": "393-450"
    "CLB 9": "371-392"
    "CLB 8": "349-370"
    "CLB 7": "310-348"
    "CLB 6": "271-309"
    "CLB 5": "226-270"
    "CLB 4": "181-225"
  
  listening:
    "CLB 10": "316-360"
    "CLB 9": "298-315"
    "CLB 8": "280-297"
    "CLB 7": "249-279"
    "CLB 6": "217-248"
    "CLB 5": "181-216"
    "CLB 4": "145-180"
  
  reading:
    "CLB 10": "263-300"
    "CLB 9": "248-262"
    "CLB 8": "233-247"
    "CLB 7": "207-232"
    "CLB 6": "181-206"
    "CLB 5": "151-180"
    "CLB 4": "121-150"
  
  writing:
    "CLB 10": "393-450"
    "CLB 9": "371-392"
    "CLB 8": "349-370"
    "CLB 7": "310-348"
    "CLB 6": "271-309"
    "CLB 5": "226-270"
    "CLB 4": "181-225"
```

---

## NOC (National Occupational Classification) System

### NOC TEER Categories
```yaml
noc_teer_system:
  teer_0:
    description: "Management occupations"
    examples: ["Senior managers", "Middle managers", "Specialized middle managers"]
  
  teer_1:
    description: "Occupations that usually require a university degree"
    examples: ["Professional occupations in business and finance", "Professional occupations in natural and applied sciences"]
  
  teer_2:
    description: "Occupations that usually require a college diploma, apprenticeship training of 2+ years, or supervisory occupations"
    examples: ["Technical occupations", "Skilled trades", "Supervisory occupations"]
  
  teer_3:
    description: "Occupations that usually require a college diploma, apprenticeship training of less than 2 years, or more than 6 months of on-the-job training"
    examples: ["Technical occupations", "Skilled trades", "Support occupations"]
  
  teer_4:
    description: "Occupations that usually require a high school diploma or several weeks of on-the-job training"
    examples: ["Intermediate occupations", "Clerical occupations"]
  
  teer_5:
    description: "Occupations that usually require short-term work demonstration or on-the-job training"
    examples: ["Labourers", "Elemental sales and service occupations"]
```

### NOC Code Structure
```yaml
noc_code_structure:
  format: "5-digit code (e.g., 21211)"
  breakdown:
    first_digit: "Broad occupational category (0-9)"
    second_digit: "TEER category (0-5)"
    remaining_digits: "Specific occupation within category"
```

---

## Proof of Funds Requirements

### Required Amounts (2024)
```yaml
proof_of_funds_2024:
  family_size_1: "$14,690 CAD"
  family_size_2: "$18,288 CAD"
  family_size_3: "$22,483 CAD"
  family_size_4: "$27,297 CAD"
  family_size_5: "$30,690 CAD"
  family_size_6: "$34,917 CAD"
  family_size_7: "$38,875 CAD"
  additional_family_member: "$3,958 CAD"

notes:
  - "Amounts updated annually"
  - "Must show funds are available and transferable"
  - "Not required if authorized to work in Canada"
  - "Not required if valid job offer in Canada"
```

---

## Common Eligibility Rules and Calculations

### Age Calculation
```yaml
age_calculation:
  reference_date: "Date application received by IRCC"
  method: "Age on reference date determines points"
  note: "Age can change between profile creation and ITA"
```

### Work Experience Calculation
```yaml
work_experience_calculation:
  full_time: "30+ hours per week"
  part_time_conversion: "Total hours ÷ 30 = weeks of full-time equivalent"
  minimum_continuous: "Must be continuous (no gaps)"
  maximum_counted: "6 years maximum for points calculation"
  
  example:
    scenario: "20 hours/week for 2 years"
    calculation: "(20 hours × 104 weeks) ÷ 30 = 69.3 weeks = 1.33 years"
```

### Education Points Calculation
```yaml
education_calculation:
  eca_required: "Yes, for foreign credentials"
  canadian_education: "No ECA required"
  multiple_credentials: "Highest level counts, plus bonus for multiple"
  incomplete_programs: "Do not count toward points"
```

### Language Test Validity
```yaml
language_test_validity:
  validity_period: "2 years from test date"
  reference_date: "Date application received by IRCC"
  retaking_tests: "Can retake to improve scores"
  mixing_tests: "Cannot mix different test types (e.g., IELTS + CELPIP)"
```

---

## CRS Score Optimization Strategies

### High-Impact Improvements
```yaml
optimization_strategies:
  provincial_nomination:
    impact: "+600 points"
    effort: "High (requires job offer or specific qualifications)"
    timeline: "6-18 months"
  
  improve_language_scores:
    impact: "Up to +50 points"
    effort: "Medium (study and retake tests)"
    timeline: "3-6 months"
  
  obtain_job_offer:
    impact: "+50-200 points"
    effort: "High (requires employer and LMIA)"
    timeline: "6-12 months"
  
  canadian_education:
    impact: "+15-30 points"
    effort: "Very High (1-4 years study)"
    timeline: "1-4 years"
  
  gain_canadian_work_experience:
    impact: "Up to +80 points"
    effort: "High (requires work permit)"
    timeline: "1-5 years"
```

### Score Improvement Calculator Logic
```yaml
score_improvement_logic:
  language_improvement:
    from_clb_6_to_7: "+8 points per ability"
    from_clb_7_to_8: "+6 points per ability"
    from_clb_8_to_9: "+7 points per ability"
    from_clb_9_to_10: "+5 points per ability"
  
  age_decline:
    annual_decrease: "5-6 points per year after age 29"
    planning_consideration: "Apply before birthday if close to cutoff"
  
  spouse_optimization:
    remove_spouse: "May increase main applicant points"
    improve_spouse_qualifications: "Up to +40 points"
```

---

## Common Calculation Errors and Validations

### Validation Rules
```yaml
validation_rules:
  age_consistency:
    - "Age must be consistent across all forms"
    - "Age calculated from birth date on reference date"
  
  work_experience_validation:
    - "Must have job letters covering claimed periods"
    - "No gaps in employment without explanation"
    - "NOC code must match job duties"
  
  language_test_validation:
    - "Test results must be within 2-year validity"
    - "All four abilities must be tested"
    - "Cannot mix different test types"
  
  education_validation:
    - "ECA required for foreign credentials"
    - "Must match claimed education level"
    - "Transcripts must support claimed credentials"
```

### Common Errors
```yaml
common_errors:
  work_experience:
    - "Claiming part-time as full-time"
    - "Including unpaid internships"
    - "Miscalculating equivalent full-time"
    - "Including self-employment without proper documentation"
  
  language_scores:
    - "Using expired test results"
    - "Mixing different test types"
    - "Claiming higher CLB than achieved"
    - "Not understanding CLB equivalencies"
  
  education:
    - "Not getting ECA for foreign credentials"
    - "Claiming incomplete programs"
    - "Misunderstanding Canadian equivalency"
    - "Not claiming multiple credentials bonus"
```

---

*This document provides detailed CRS scoring and eligibility information for system development purposes. CRS scoring rules and eligibility criteria change frequently. Always consult current IRCC resources and qualified immigration professionals for up-to-date information.*

**Document Version:** 1.0  
**Last Updated:** 2025-11-17  
**Next Review:** 2025-12-17