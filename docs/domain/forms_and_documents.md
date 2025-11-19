# Immigration Forms and Documents

## Document Purpose

This document provides comprehensive information about Canadian immigration forms and required documents for system development purposes. It includes form specifications, document requirements, and validation criteria for AI agent training.

**⚠️ DISCLAIMER: This document is for product development purposes only and does not constitute legal advice. Forms and document requirements change frequently. Always consult current IRCC resources and qualified immigration professionals for legal guidance.**

---

## IRCC Form Categories

### Form Classification System
```yaml
form_categories:
  permanent_residence:
    - "Generic application forms"
    - "Schedule forms (program-specific)"
    - "Background and declaration forms"
    - "Family information forms"
  
  temporary_residence:
    - "Visitor visa applications"
    - "Work permit applications"
    - "Study permit applications"
    - "Extension and change of status"
  
  supporting_forms:
    - "Representative forms"
    - "Statutory declarations"
    - "Medical forms"
    - "Police certificate forms"
```

---

## Permanent Residence Forms

### IMM 0008 - Generic Application Form for Canada

#### Form Details
```yaml
imm_0008:
  title: "Generic Application Form for Canada"
  purpose: "Main application form for permanent residence"
  pages: "6 pages"
  language: "English or French"
  
  sections:
    personal_details:
      - "Full name and aliases"
      - "Date and place of birth"
      - "Gender and marital status"
      - "Contact information"
    
    background_information:
      - "Citizenship and nationality"
      - "Language abilities"
      - "Education history"
      - "Current occupation"
    
    immigration_details:
      - "Immigration category"
      - "Intended destination in Canada"
      - "Funds available"
      - "Previous applications to Canada"
```

#### Field Specifications
```yaml
imm_0008_fields:
  family_name:
    type: "Text"
    max_length: 50
    required: true
    validation: "Letters, hyphens, apostrophes, spaces only"
  
  given_names:
    type: "Text"
    max_length: 50
    required: true
    validation: "Letters, hyphens, apostrophes, spaces only"
  
  date_of_birth:
    type: "Date"
    format: "YYYY-MM-DD"
    required: true
    validation: "Must be valid date, applicant must be 18+"
  
  country_of_birth:
    type: "Dropdown"
    required: true
    options: "ISO country codes"
  
  current_country_of_residence:
    type: "Dropdown"
    required: true
    options: "ISO country codes"
```

### IMM 5669 - Schedule A - Background/Declaration

#### Form Details
```yaml
imm_5669:
  title: "Schedule A - Background/Declaration"
  purpose: "Detailed background information and declarations"
  pages: "4 pages"
  required_for: "All applicants 18 years and older"
  
  sections:
    personal_history:
      - "10-year personal history (no gaps)"
      - "Education history"
      - "Employment history"
      - "Addresses lived at"
    
    background_questions:
      - "Military service"
      - "Government positions"
      - "Membership in organizations"
      - "Criminal history"
    
    declarations:
      - "Health conditions"
      - "Immigration violations"
      - "Refused visas"
      - "Deportation history"
```

#### Personal History Requirements
```yaml
personal_history_requirements:
  time_period: "10 years or since 18th birthday, whichever is more recent"
  no_gaps: "Every month must be accounted for"
  categories:
    - "Education"
    - "Employment"
    - "Unemployment"
    - "Military service"
    - "Other activities"
  
  required_information:
    - "Start and end dates (YYYY-MM)"
    - "Activity type"
    - "Name of institution/employer"
    - "City and country"
    - "Position/field of study"
```

### IMM 5406 - Additional Family Information

#### Form Details
```yaml
imm_5406:
  title: "Additional Family Information"
  purpose: "Detailed family member information"
  pages: "2 pages"
  required_for: "Principal applicant and spouse/partner"
  
  family_members_included:
    - "Parents"
    - "Siblings"
    - "Children"
    - "Spouse/common-law partner"
    - "Former spouses"
  
  required_information:
    - "Full name"
    - "Relationship to applicant"
    - "Date of birth"
    - "Country of birth"
    - "Current address"
    - "Marital status"
```

### IMM 5476 - Use of a Representative

#### Form Details
```yaml
imm_5476:
  title: "Use of a Representative"
  purpose: "Authorize representative to act on behalf of applicant"
  pages: "2 pages"
  required_when: "Using immigration consultant or lawyer"
  
  representative_types:
    paid_representatives:
      - "Immigration consultants (RCIC)"
      - "Lawyers"
      - "Quebec notaries"
    
    unpaid_representatives:
      - "Family members"
      - "Friends"
      - "Organizations"
  
  authorization_scope:
    - "Receive information about application"
    - "Submit documents on behalf of applicant"
    - "Represent at interviews"
    - "Receive decisions and correspondence"
```

---

## Program-Specific Schedule Forms

### Express Entry Schedules

#### IMM 5612 - Schedule 4 - Economic Classes - Federal Skilled Workers
```yaml
imm_5612:
  title: "Schedule 4 - Economic Classes - Federal Skilled Workers"
  purpose: "FSW-specific information"
  required_for: "Federal Skilled Worker applicants"
  
  sections:
    work_experience:
      - "Detailed work history"
      - "NOC codes and job duties"
      - "Employment verification"
    
    language_proficiency:
      - "Test results and scores"
      - "Test dates and validity"
    
    education:
      - "Educational credentials"
      - "ECA report details"
    
    funds:
      - "Proof of funds documentation"
      - "Source of funds"
```

#### IMM 5710 - Schedule 8 - Economic Classes - Canadian Experience Class
```yaml
imm_5710:
  title: "Schedule 8 - Economic Classes - Canadian Experience Class"
  purpose: "CEC-specific information"
  required_for: "Canadian Experience Class applicants"
  
  canadian_experience_details:
    - "Canadian work experience"
    - "Work permit details"
    - "Employer information"
    - "Job duties and NOC classification"
```

### Provincial Nominee Schedules

#### IMM 5690 - Schedule 4 - Economic Classes - Provincial Nominees
```yaml
imm_5690:
  title: "Schedule 4 - Economic Classes - Provincial Nominees"
  purpose: "PNP-specific information"
  required_for: "Provincial nominee applicants"
  
  nomination_details:
    - "Provincial nomination certificate"
    - "Nominating province/territory"
    - "Nomination stream"
    - "Job offer details (if applicable)"
```

---

## Temporary Residence Forms

### IMM 5257 - Application for Temporary Resident Visa

#### Form Details
```yaml
imm_5257:
  title: "Application for Temporary Resident Visa"
  purpose: "Visitor visa applications"
  pages: "4 pages"
  
  sections:
    applicant_information:
      - "Personal details"
      - "Contact information"
      - "Passport information"
    
    travel_information:
      - "Purpose of visit"
      - "Duration of stay"
      - "Intended date of arrival"
      - "Places to visit in Canada"
    
    background_information:
      - "Previous travel to Canada"
      - "Family in Canada"
      - "Employment and education"
      - "Financial information"
```

### IMM 1294 - Application to Change Conditions, Extend Stay or Remain in Canada

#### Form Details
```yaml
imm_1294:
  title: "Application to Change Conditions, Extend Stay or Remain in Canada"
  purpose: "Work permits, study permits, visitor extensions"
  pages: "5 pages"
  
  application_types:
    - "Work permit (initial or extension)"
    - "Study permit (initial or extension)"
    - "Visitor record (extension of stay)"
    - "Change of conditions"
  
  required_information:
    - "Current status in Canada"
    - "Requested new status or extension"
    - "Supporting documents"
    - "Fees and payment information"
```

---

## Supporting Documents by Program

### Express Entry Documents

#### Identity and Civil Status Documents
```yaml
identity_documents:
  passport:
    requirement: "Biographical pages of current passport"
    validity: "Must be valid for travel"
    notes: "All family members included in application"
  
  birth_certificate:
    requirement: "Official birth certificate"
    issued_by: "Vital statistics office"
    translation: "Required if not in English or French"
  
  marriage_certificate:
    requirement: "If married - official marriage certificate"
    issued_by: "Civil registration authority"
    translation: "Required if not in English or French"
  
  divorce_decree:
    requirement: "If divorced - final divorce decree"
    issued_by: "Court or civil authority"
    translation: "Required if not in English or French"
  
  death_certificate:
    requirement: "If widowed - death certificate of spouse"
    issued_by: "Vital statistics office"
    translation: "Required if not in English or French"
```

#### Education Documents
```yaml
education_documents:
  educational_credential_assessment:
    requirement: "ECA report for foreign credentials"
    valid_organizations:
      - "WES (World Education Services)"
      - "ICAS (International Credential Assessment Service)"
      - "CES (Comparative Education Service)"
      - "IQAS (International Qualifications Assessment Service)"
      - "PEBC (Pharmacy Examining Board of Canada)"
      - "MCC (Medical Council of Canada)"
    validity: "5 years from issue date"
  
  diplomas_degrees:
    requirement: "Official transcripts and diplomas"
    issued_by: "Educational institution"
    translation: "Required if not in English or French"
    notes: "Must include all post-secondary education"
  
  transcripts:
    requirement: "Official transcripts"
    format: "Sealed envelope from institution"
    content: "All courses, grades, graduation date"
```

#### Language Test Results
```yaml
language_documents:
  english_tests:
    ielts:
      full_name: "International English Language Testing System"
      test_type: "General Training"
      validity: "2 years"
      required_scores: "All four abilities tested"
    
    celpip:
      full_name: "Canadian English Language Proficiency Index Program"
      test_type: "CELPIP-General"
      validity: "2 years"
      required_scores: "All four abilities tested"
  
  french_tests:
    tef:
      full_name: "Test d'évaluation de français"
      test_type: "TEF Canada"
      validity: "2 years"
      required_scores: "All four abilities tested"
    
    tcf:
      full_name: "Test de connaissance du français"
      test_type: "TCF Canada"
      validity: "2 years"
      required_scores: "All four abilities tested"
```

#### Work Experience Documents
```yaml
work_experience_documents:
  reference_letters:
    requirement: "Letter from each employer"
    letterhead: "Official company letterhead"
    signatory: "HR officer or immediate supervisor"
    
    required_content:
      - "Job title and duties"
      - "Employment dates"
      - "Number of hours worked per week"
      - "Annual salary and benefits"
      - "Contact information of signatory"
  
  employment_contracts:
    requirement: "If available"
    purpose: "Support reference letters"
    translation: "Required if not in English or French"
  
  pay_stubs:
    requirement: "If available"
    purpose: "Verify salary information"
    period: "Recent pay stubs covering employment period"
  
  tax_documents:
    requirement: "If available"
    types: "T4 slips, tax returns, employment insurance records"
    purpose: "Verify employment and income"
```

#### Proof of Funds
```yaml
proof_of_funds_documents:
  bank_statements:
    requirement: "Official bank statements"
    period: "Last 6 months"
    currency: "Show amounts in original currency and CAD equivalent"
    
    required_information:
      - "Account holder name"
      - "Account number"
      - "Bank contact information"
      - "Account balance and transaction history"
  
  bank_letters:
    requirement: "Official letter from financial institution"
    letterhead: "Bank letterhead"
    
    required_content:
      - "Account holder name"
      - "Account numbers"
      - "Date accounts opened"
      - "Current balance"
      - "Average balance for past 6 months"
  
  investment_documents:
    types: "GICs, term deposits, mutual funds, stocks"
    requirement: "Official statements showing current value"
    liquidity: "Must be readily convertible to cash"
```

### Medical Examinations

#### Medical Exam Requirements
```yaml
medical_exam_requirements:
  when_required:
    - "All permanent residence applicants"
    - "Temporary residents from certain countries"
    - "Work in health services, child care, or primary/secondary education"
  
  designated_medical_practitioners:
    requirement: "Must use IRCC-approved panel physician"
    location: "Available in most countries worldwide"
    appointment: "Book directly with panel physician"
  
  exam_components:
    - "Medical history review"
    - "Physical examination"
    - "Chest X-ray (11 years and older)"
    - "Blood tests (15 years and older)"
    - "Urine test (5 years and older)"
  
  validity: "12 months from exam date"
```

### Police Certificates

#### Police Certificate Requirements
```yaml
police_certificate_requirements:
  when_required:
    - "All countries where lived 6+ months since age 18"
    - "Current country of residence"
    - "Country of citizenship (if different)"
  
  validity: "Generally 1 year from issue date"
  
  country_specific_requirements:
    canada:
      type: "RCMP criminal record check"
      fingerprints: "Required if lived in Canada"
    
    united_states:
      type: "FBI Identity History Summary Check"
      fingerprints: "Required"
    
    united_kingdom:
      type: "ACRO Police Certificate"
      online_application: "Available"
    
    india:
      type: "Police Clearance Certificate"
      issued_by: "Regional Passport Office"
```

---

## Document Specifications and Standards

### General Document Requirements

#### Format and Quality Standards
```yaml
document_standards:
  format:
    - "PDF format preferred for digital submissions"
    - "High-resolution scans (300 DPI minimum)"
    - "Color scans for documents with color elements"
    - "Black and white acceptable for text documents"
  
  quality:
    - "All text must be clearly legible"
    - "No shadows or distortions"
    - "Complete document visible (no cut-off edges)"
    - "Proper orientation (not rotated)"
  
  size_limits:
    individual_file: "4 MB maximum"
    total_submission: "Varies by application type"
    pages: "Single-page documents preferred"
```

#### Translation Requirements
```yaml
translation_requirements:
  when_required:
    - "Documents not in English or French"
    - "All supporting documents must be translated"
  
  certified_translation:
    requirement: "Must be certified translation"
    translator_qualifications:
      - "Member of provincial or territorial translation association"
      - "Certified by Canadian Translators, Terminologists and Interpreters Council"
    
    affidavit_content:
      - "Translator's name and contact information"
      - "Statement of accuracy"
      - "Date of translation"
      - "Translator's signature and seal"
  
  original_documents:
    requirement: "Submit both original and translation"
    format: "Certified copies acceptable"
```

### Digital Submission Requirements

#### Online Portal Specifications
```yaml
digital_submission:
  file_formats:
    accepted: ["PDF", "JPG", "JPEG", "PNG", "TIFF"]
    preferred: "PDF"
    not_accepted: ["DOC", "DOCX", "XLS", "XLSX"]
  
  file_naming:
    convention: "Descriptive names in English"
    examples:
      - "Passport_John_Smith.pdf"
      - "Degree_Certificate_Jane_Doe.pdf"
      - "Reference_Letter_ABC_Company.pdf"
  
  upload_process:
    - "Log into online account"
    - "Navigate to document upload section"
    - "Select document type from dropdown"
    - "Upload file and verify preview"
    - "Submit and confirm receipt"
```

---

## Form Completion Guidelines

### Common Form Fields

#### Name Fields
```yaml
name_field_guidelines:
  family_name:
    definition: "Surname or last name"
    multiple_names: "Use primary surname if multiple"
    no_surname: "Enter given name in both fields"
  
  given_names:
    definition: "First and middle names"
    order: "As shown on passport or birth certificate"
    abbreviations: "Spell out abbreviated names"
  
  aliases:
    include: "All names ever used"
    examples: "Maiden names, nicknames, professional names"
    format: "Separate multiple aliases with semicolons"
```

#### Date Fields
```yaml
date_field_guidelines:
  format: "YYYY-MM-DD"
  unknown_dates:
    year_only: "Use January 1st (YYYY-01-01)"
    month_year: "Use first day of month (YYYY-MM-01)"
  
  validation:
    - "Must be valid calendar date"
    - "Birth date must result in age 18+ for main applicant"
    - "Future dates not allowed except for intended travel"
```

#### Address Fields
```yaml
address_field_guidelines:
  current_address:
    requirement: "Where you currently live"
    po_box: "Not acceptable as primary address"
    format: "Street number, street name, apartment/unit"
  
  mailing_address:
    purpose: "Where IRCC should send correspondence"
    same_as_current: "Check box if same as current address"
    representative: "Can use representative's address"
  
  international_addresses:
    format: "Use local format for country"
    postal_code: "Include if applicable"
    translation: "Provide English translation if needed"
```

### Form Validation Rules

#### Required Field Validation
```yaml
validation_rules:
  mandatory_fields:
    - "Cannot be left blank"
    - "Must select from dropdown options"
    - "Date fields must be complete"
  
  conditional_requirements:
    spouse_information: "Required if married or common-law"
    children_information: "Required if have dependent children"
    representative_info: "Required if using representative"
  
  consistency_checks:
    - "Dates must be in logical order"
    - "Information must match across forms"
    - "Supporting documents must align with form data"
```

---

## Document Checklists by Program

### Express Entry Document Checklist
```yaml
express_entry_checklist:
  identity_documents:
    - "Passport biographical pages"
    - "Birth certificate"
    - "Marriage certificate (if applicable)"
    - "Divorce decree (if applicable)"
  
  education_documents:
    - "Educational Credential Assessment (ECA)"
    - "Diplomas and degrees"
    - "Official transcripts"
  
  language_documents:
    - "Language test results (IELTS, CELPIP, TEF, or TCF)"
  
  work_experience_documents:
    - "Reference letters from employers"
    - "Employment contracts (if available)"
    - "Pay stubs (if available)"
  
  proof_of_funds:
    - "Bank statements (6 months)"
    - "Bank letter"
    - "Investment statements (if applicable)"
  
  additional_documents:
    - "Police certificates"
    - "Medical exam results"
    - "Provincial nomination certificate (if applicable)"
    - "Job offer letter (if applicable)"
```

### Family Class Sponsorship Checklist
```yaml
family_class_checklist:
  sponsor_documents:
    - "Proof of Canadian citizenship or permanent residence"
    - "Identity documents"
    - "Proof of income (3 years)"
    - "Tax returns and assessments"
  
  sponsored_person_documents:
    - "Identity and civil status documents"
    - "Police certificates"
    - "Medical exam results"
    - "Photos"
  
  relationship_documents:
    spouse_partner:
      - "Marriage certificate or proof of common-law relationship"
      - "Joint bank accounts, leases, insurance"
      - "Photos together"
      - "Communication records"
    
    parent_grandparent:
      - "Birth certificate showing relationship"
      - "Proof of sponsor's birth in Canada or immigration"
```

---

## Quality Assurance and Common Errors

### Document Quality Issues
```yaml
common_quality_issues:
  scanning_problems:
    - "Blurry or illegible text"
    - "Shadows or reflections"
    - "Cut-off edges or missing content"
    - "Wrong orientation"
  
  format_issues:
    - "Unsupported file formats"
    - "File size too large"
    - "Multiple documents in single file"
    - "Poor image resolution"
  
  content_issues:
    - "Missing pages or sections"
    - "Outdated or expired documents"
    - "Incorrect document type"
    - "Missing translations"
```

### Form Completion Errors
```yaml
common_form_errors:
  information_inconsistency:
    - "Names spelled differently across forms"
    - "Dates don't match supporting documents"
    - "Address information inconsistent"
  
  missing_information:
    - "Blank required fields"
    - "Incomplete personal history"
    - "Missing family member information"
  
  validation_errors:
    - "Invalid date formats"
    - "Incorrect dropdown selections"
    - "Mathematical errors in calculations"
```

---

*This document provides comprehensive information about Canadian immigration forms and documents for system development purposes. Forms and requirements change frequently. Always consult current IRCC resources and qualified immigration professionals for up-to-date information.*

**Document Version:** 1.0  
**Last Updated:** 2025-11-17  
**Next Review:** 2025-12-17