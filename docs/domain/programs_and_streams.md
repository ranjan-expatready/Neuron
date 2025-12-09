# Immigration Programs and Streams

## Document Purpose

This document provides detailed information about Canadian immigration programs and streams for system development purposes. It covers eligibility requirements, application processes, and key considerations for each major program.

**⚠️ DISCLAIMER: This document is for product development purposes only and does not constitute legal advice. Immigration laws and policies change frequently. Always consult current IRCC resources and qualified immigration professionals for legal guidance.**

---

## Express Entry Programs

### Federal Skilled Worker Program (FSW)

#### Eligibility Requirements
```yaml
fsw_requirements:
  minimum_requirements:
    work_experience: "1 year continuous full-time (or equivalent part-time)"
    language_ability: "CLB 7 in English or French"
    education: "Canadian secondary (high school) or equivalent foreign credential"
    proof_of_funds: "Sufficient funds to support family"
    admissibility: "No criminal record, pass medical exam"
  
  points_system:
    minimum_score: "67 out of 100 points"
    factors:
      education: "Maximum 25 points"
      language: "Maximum 28 points (24 first language + 4 second)"
      work_experience: "Maximum 15 points"
      age: "Maximum 12 points"
      arranged_employment: "Maximum 10 points"
      adaptability: "Maximum 10 points"
```

#### Work Experience Requirements
- **Skill Type:** NOC TEER 0, 1, 2, or 3
- **Duration:** Minimum 1 year continuous full-time or equivalent part-time
- **Recency:** Within the last 10 years
- **Paid Work:** Must be paid work (volunteer work doesn't count)

#### Language Requirements
- **First Official Language:** Minimum CLB 7 in all four abilities
- **Second Official Language:** Not required but can earn additional points
- **Accepted Tests:** IELTS, CELPIP (English), TEF, TCF (French)

### Canadian Experience Class (CEC)

#### Eligibility Requirements
```yaml
cec_requirements:
  work_experience:
    duration: "Minimum 1 year full-time (or equivalent part-time)"
    location: "In Canada"
    authorization: "With proper work authorization"
    skill_level: "NOC TEER 0, 1, 2, or 3"
    recency: "Within 3 years before application"
  
  language_requirements:
    noc_0_1: "CLB 7 in English or French"
    noc_2_3: "CLB 5 in English or French"
  
  education:
    requirement: "Not required but affects CRS score"
    recommendation: "Get Educational Credential Assessment (ECA)"
```

#### Canadian Work Experience Types
- **Full-time:** 30+ hours per week
- **Part-time:** Less than 30 hours per week (calculate equivalent)
- **Multiple Jobs:** Can combine different jobs if all meet requirements
- **Self-employment:** Does not count toward CEC requirements

### Federal Skilled Trades Program (FST)

#### Eligibility Requirements
```yaml
fst_requirements:
  work_experience:
    duration: "Minimum 2 years full-time (or equivalent part-time)"
    recency: "Within 5 years before application"
    skill_level: "NOC TEER 2 or 3 in eligible trades"
  
  language_requirements:
    speaking_listening: "CLB 5 in English or French"
    reading_writing: "CLB 4 in English or French"
  
  job_offer_or_certificate:
    option_1: "Valid job offer for full-time employment for at least 1 year"
    option_2: "Certificate of qualification in skilled trade from Canadian authority"
  
  education:
    requirement: "Not required but may improve CRS score"
```

#### Eligible Skilled Trades
```yaml
eligible_trades:
  major_group_72:
    - "Industrial, electrical and construction trades"
    - "Electricians, plumbers, welders"
    - "Heavy equipment operators"
  
  major_group_73:
    - "Maintenance and equipment operation trades"
    - "Power engineers, water treatment operators"
    - "Refrigeration and air conditioning mechanics"
  
  major_group_82:
    - "Supervisors and technical jobs in natural resources"
    - "Agriculture and related production"
    - "Processing, manufacturing and utilities supervisors"
  
  major_group_92:
    - "Processing, manufacturing and utilities supervisors"
    - "Central control and process operators"
    - "Aircraft assemblers and aircraft assembly inspectors"
  
  minor_group_632:
    - "Chefs and cooks"
    - "Butchers and bakers"
```

---

## Provincial Nominee Program (PNP) Details

### Ontario Immigrant Nominee Program (OINP)

#### Human Capital Priorities Stream
```yaml
oinp_human_capital:
  eligibility:
    express_entry: "Must have active Express Entry profile"
    crs_score: "Minimum score varies by draw (typically 400+)"
    language: "CLB 7 in English or French"
    education: "Bachelor's degree or higher"
    work_experience: "1 year in NOC TEER 0, 1, 2, or 3"
  
  targeted_occupations:
    - "Information technology"
    - "Healthcare"
    - "Engineering"
    - "Skilled trades"
    - "Business and finance"
```

#### Employer Job Offer Streams
```yaml
oinp_employer_streams:
  foreign_worker:
    job_offer: "Permanent, full-time in Ontario"
    wage: "At or above median wage for occupation"
    experience: "2 years in occupation within 5 years"
    language: "CLB 5 (NOC TEER 2, 3) or CLB 7 (NOC TEER 0, 1)"
  
  in_demand_skills:
    job_offer: "Permanent, full-time in specific occupations"
    occupations: "Agriculture, construction, trucking, personal support"
    experience: "9 months in Ontario in last 3 years"
    language: "CLB 4 in English or French"
  
  international_student:
    education: "Completed eligible program at Ontario institution"
    job_offer: "Permanent, full-time, related to field of study"
    language: "CLB 7 (NOC TEER 0, 1) or CLB 5 (NOC TEER 2, 3)"
```

### British Columbia Provincial Nominee Program (BC PNP)

#### Skills Immigration Categories
```yaml
bc_pnp_skills:
  skilled_worker:
    job_offer: "Indeterminate, full-time from BC employer"
    experience: "2 years directly related work experience"
    language: "CLB 4 minimum"
    education: "Post-secondary credential"
    wage: "Competitive wage for occupation and region"
  
  healthcare_professional:
    job_offer: "From BC public health authority"
    eligibility: "Eligible to work as healthcare professional in BC"
    experience: "2 years as healthcare professional"
    language: "CLB 4 minimum"
  
  international_graduate:
    education: "Degree, diploma, or certificate from eligible Canadian institution"
    job_offer: "Indeterminate, full-time from BC employer"
    language: "CLB 4 minimum"
    graduation: "Within 3 years of graduation"
  
  international_post_graduate:
    education: "Master's or PhD from eligible BC institution"
    field_of_study: "Natural, applied, or health sciences"
    graduation: "Within 3 years of graduation"
    job_offer: "Not required"
```

#### Express Entry BC Categories
- Same requirements as Skills Immigration categories
- Must have active Express Entry profile
- Faster processing through Express Entry system

### Alberta Immigrant Nominee Program (AINP)

#### Alberta Opportunity Stream
```yaml
ainp_opportunity:
  eligibility:
    work_experience: "18 months full-time in Alberta in eligible occupation"
    job_offer: "Full-time permanent from Alberta employer"
    language: "CLB 4 in English or French"
    education: "High school or higher"
    intention: "Intention to live permanently in Alberta"
  
  eligible_occupations:
    - "NOC TEER 0, 1, 2, 3, 4, or 5"
    - "Some restrictions apply to certain occupations"
```

#### Alberta Express Entry Stream
```yaml
ainp_express_entry:
  eligibility:
    express_entry: "Active Express Entry profile"
    crs_score: "Minimum 300 points"
    connection_to_alberta:
      - "Work experience in Alberta"
      - "Job offer from Alberta employer"
      - "Family member in Alberta"
      - "Education in Alberta"
    language: "CLB 5 minimum"
```

---

## Family Class Immigration

### Spouse, Partner, and Children

#### Eligible Relationships
```yaml
eligible_relationships:
  spouse:
    - "Legally married"
    - "Marriage recognized in country where it took place"
    - "Marriage recognized under Canadian law"
  
  common_law_partner:
    - "Living together continuously for at least 1 year"
    - "In conjugal relationship"
    - "Not married to each other or anyone else"
  
  conjugal_partner:
    - "In relationship for at least 1 year"
    - "Cannot live together due to circumstances beyond control"
    - "Relationship similar to marriage or common-law"
  
  dependent_children:
    - "Under 22 years old"
    - "Not married or in common-law relationship"
    - "22 or older if dependent due to mental or physical condition"
```

#### Sponsor Requirements
```yaml
sponsor_requirements:
  eligibility:
    - "Canadian citizen or permanent resident"
    - "18 years of age or older"
    - "Not receiving social assistance (except disability)"
    - "Not in prison, bankrupt, or under removal order"
  
  undertaking:
    duration: "3 years (spouse/partner), 10 years (children under 22), 20 years (children 22+)"
    responsibilities: "Provide basic needs, repay social assistance"
    co_signer: "Required in Quebec for some relationships"
  
  financial_requirements:
    income: "Meet minimum necessary income (varies by family size)"
    proof: "3 years of tax returns and employment information"
```

### Parents and Grandparents Program (PGP)

#### Sponsor Requirements
```yaml
pgp_sponsor_requirements:
  income:
    requirement: "Meet minimum necessary income for 3 consecutive years"
    calculation: "Based on family size including sponsored persons"
    increase: "30% above Low Income Cut-Off (LICO)"
  
  undertaking:
    duration: "20 years"
    responsibilities: "Provide basic needs, healthcare costs not covered by provincial plan"
  
  application_process:
    step_1: "Submit interest to sponsor form (when open)"
    step_2: "Invitation to apply (if selected in lottery)"
    step_3: "Submit complete application within 60 days"
```

#### Processing and Alternatives
- **Processing Time:** 20-24 months
- **Alternative:** Super Visa (multiple-entry visa valid up to 10 years)

---

## Business and Investor Programs

### Start-up Visa Program

#### Requirements
```yaml
startup_visa_requirements:
  business_idea:
    - "Innovative business idea"
    - "Can create jobs for Canadians"
    - "Can compete globally"
  
  support:
    - "Letter of support from designated organization"
    - "Venture capital fund: minimum $200,000 investment"
    - "Angel investor group: minimum $75,000 investment"
    - "Business incubator: acceptance into program"
  
  language:
    - "CLB 5 in English or French in all four abilities"
  
  education:
    - "Completed at least 1 year of post-secondary education"
  
  funds:
    - "Sufficient settlement funds"
```

### Self-employed Persons Program

#### Eligibility
```yaml
self_employed_requirements:
  experience:
    - "2 years of self-employment in cultural or athletic activities"
    - "2 years of experience in farm management"
    - "1 year self-employment + 1 year participation at world-class level"
  
  intention:
    - "Create own employment in Canada"
    - "Make significant contribution to cultural/athletic life or farming"
  
  selection_factors:
    - "Experience (35 points)"
    - "Education (25 points)"
    - "Age (10 points)"
    - "Language abilities (24 points)"
    - "Adaptability (6 points)"
    - "Pass mark: 35 points"
```

---

## Caregiver Programs

### Home Child Care Provider Pilot

#### Requirements
```yaml
childcare_pilot_requirements:
  work_experience:
    - "24 months full-time equivalent in last 4 years"
    - "Caring for children under 18 in private home"
  
  education:
    - "1-year post-secondary credential"
    - "OR completion of high school + 6 months training"
  
  language:
    - "CLB 5 in English or French"
  
  job_offer:
    - "Full-time job offer for at least 1 year"
    - "Caring for child under 18 in private home"
```

### Home Support Worker Pilot

#### Requirements
```yaml
support_worker_pilot_requirements:
  work_experience:
    - "24 months full-time equivalent in last 4 years"
    - "Providing care to seniors, persons with disabilities, or chronic illness"
  
  education:
    - "1-year post-secondary credential"
    - "OR completion of high school + 6 months training"
  
  language:
    - "CLB 5 in English or French"
  
  job_offer:
    - "Full-time job offer for at least 1 year"
    - "Providing care in private home"
```

---

## Temporary Residence Programs

### International Mobility Program (IMP)

#### LMIA-Exempt Categories
```yaml
imp_categories:
  international_agreements:
    nafta_usmca:
      - "Business visitors"
      - "Professionals"
      - "Intra-company transferees"
    
    ceta:
      - "Business visitors from EU"
      - "Professionals and skilled workers"
    
    cptpp:
      - "Business persons from CPTPP countries"
  
  canadian_interests:
    significant_benefit:
      - "Unique skills or knowledge"
      - "Reciprocal employment"
      - "Designated by province"
    
    intra_company_transfers:
      - "Executives and senior managers"
      - "Specialized knowledge workers"
      - "Minimum 1 year employment with company"
  
  international_experience:
    - "International Experience Canada (IEC)"
    - "Working Holiday"
    - "Young Professionals"
    - "International Co-op"
```

### Temporary Foreign Worker Program (TFWP)

#### LMIA Requirements
```yaml
lmia_requirements:
  labour_market_test:
    - "Advertise position to Canadians first"
    - "Minimum 4 weeks advertising"
    - "Use Job Bank and other recruitment methods"
  
  wage_requirements:
    - "Pay prevailing wage for occupation and region"
    - "Provide same working conditions as Canadians"
  
  transition_plan:
    - "Plan to reduce reliance on temporary foreign workers"
    - "Activities to recruit and train Canadians"
```

---

## Quebec Immigration Programs

### Quebec-Selected Skilled Workers

#### Selection Process
```yaml
quebec_skilled_workers:
  step_1:
    - "Submit application to Quebec government"
    - "Assessed using Quebec selection factors"
    - "Receive Certificat de sélection du Québec (CSQ)"
  
  step_2:
    - "Apply to IRCC for permanent residence"
    - "Medical exams and background checks"
    - "Final approval by federal government"
  
  selection_factors:
    - "Education and training"
    - "Work experience"
    - "Age"
    - "Language proficiency (French and English)"
    - "Connection to Quebec"
    - "Spouse characteristics"
    - "Financial self-sufficiency"
```

### Quebec Experience Program (PEQ)

#### Categories
```yaml
peq_categories:
  quebec_graduate:
    - "Completed eligible Quebec program"
    - "French proficiency (intermediate level)"
    - "Intention to live in Quebec"
  
  temporary_worker:
    - "12 months full-time work experience in Quebec"
    - "French proficiency (intermediate level)"
    - "Valid work permit"
```

---

## Atlantic Immigration Program (AIP)

### Program Overview
```yaml
aip_overview:
  participating_provinces:
    - "Nova Scotia"
    - "New Brunswick"
    - "Prince Edward Island"
    - "Newfoundland and Labrador"
  
  categories:
    - "Atlantic High-Skilled Program"
    - "Atlantic Intermediate-Skilled Program"
    - "Atlantic International Graduate Program"
```

### Requirements
```yaml
aip_requirements:
  job_offer:
    - "From designated employer in Atlantic Canada"
    - "Full-time, non-seasonal, at least 1 year"
  
  work_experience:
    high_skilled: "1 year in NOC TEER 0, 1, 2, or 3"
    intermediate_skilled: "1 year in NOC TEER 0, 1, 2, 3, or 4"
    international_graduate: "No work experience required"
  
  education:
    high_skilled: "High school diploma or higher"
    intermediate_skilled: "High school diploma or higher"
    international_graduate: "Degree, diploma, or certificate from recognized Atlantic Canadian institution"
  
  language:
    high_skilled: "CLB 5 in English or French"
    intermediate_skilled: "CLB 4 in English or French"
    international_graduate: "CLB 5 in English or French"
  
  settlement_plan:
    - "Settlement plan developed with settlement service provider"
    - "Connection to settlement services in Atlantic Canada"
```

---

## Rural and Northern Immigration Pilot (RNIP)

### Participating Communities
```yaml
rnip_communities:
  - "Moose Jaw, Saskatchewan"
  - "Claresholm, Alberta"
  - "Vernon, British Columbia"
  - "West Kootenay, British Columbia"
  - "Altona/Rhineland, Manitoba"
  - "Brandon, Manitoba"
  - "Gretna-Rhineland-Altona-Plum Coulee, Manitoba"
  - "North Bay, Ontario"
  - "Sudbury, Ontario"
  - "Timmins, Ontario"
  - "Thunder Bay, Ontario"
```

### Requirements
```yaml
rnip_requirements:
  job_offer:
    - "From employer in participating community"
    - "Full-time, non-seasonal, permanent"
    - "Meet community-specific requirements"
  
  work_experience:
    - "1 year continuous work experience in last 3 years"
    - "NOC TEER 0, 1, 2, 3, 4, or 5"
  
  education:
    - "High school diploma or higher"
    - "Educational Credential Assessment if educated outside Canada"
  
  language:
    - "CLB 4 in English or French"
    - "Higher levels may be required for certain occupations"
  
  community_recommendation:
    - "Recommendation from participating community"
    - "Meet community-specific criteria"
    - "Demonstrate intention to live in community"
```

---

## Program Comparison Matrix

### Processing Times
```yaml
processing_times_comparison:
  express_entry: "6 months (after ITA)"
  pnp_paper_based: "18-20 months"
  pnp_express_entry: "6 months (after provincial nomination)"
  family_class_spouse: "12 months"
  family_class_pgp: "20-24 months"
  startup_visa: "12-16 months"
  self_employed: "35 months"
  caregiver_pilots: "12 months"
  atlantic_immigration: "6 months"
  quebec_skilled_worker: "12-18 months"
```

### Investment Requirements
```yaml
investment_requirements:
  startup_visa:
    venture_capital: "$200,000 minimum"
    angel_investor: "$75,000 minimum"
    incubator: "No investment required"
  
  provincial_investor_programs:
    quebec_investor: "$1.2 million (5-year loan)"
    quebec_entrepreneur: "$300,000-$500,000"
  
  self_employed: "No specific investment requirement"
```

### Language Requirements Summary
```yaml
language_requirements_summary:
  clb_7_required:
    - "Federal Skilled Worker"
    - "Canadian Experience Class (NOC TEER 0, 1)"
    - "Most PNP streams"
  
  clb_5_required:
    - "Canadian Experience Class (NOC TEER 2, 3)"
    - "Start-up Visa"
    - "Some PNP streams"
  
  clb_4_required:
    - "Federal Skilled Trades (reading/writing)"
    - "Some PNP streams"
    - "Rural and Northern Immigration Pilot"
```

---

*This document provides detailed information about Canadian immigration programs for system development purposes. Immigration requirements and processes change frequently. Always consult current IRCC resources and qualified immigration professionals for up-to-date information.*

**Document Version:** 1.0  
**Last Updated:** 2025-11-17  
**Next Review:** 2025-12-17