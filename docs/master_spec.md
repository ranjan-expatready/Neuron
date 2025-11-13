
📘 CANADA IMMIGRATION OS — MASTER SPEC (v1.0)

A Multi-Agent, Self-Evolving SaaS Platform for Canadian Immigration Consultants

Audience:

Autonomous engineering agents (OpenHands, MCP-based agents)

Human architects, CTOs, product managers


Goal:
Enable OpenHands to build, evolve, and maintain a world-class, compliant Canada Immigration OS with minimal human coding, while keeping humans fully in control of law/rule approval and key product decisions.


---

0. Document Usage (For OpenHands & Other Agents)

You (the AI engineer) MUST:

1. Treat this document as the primary specification.


2. Never invent immigration law or rules.


3. Implement systems so that:

Only human-approved rules are used to assess eligibility.

All high-risk actions are auditable and reversible.



4. Use MCP servers for:

GitHub, DB, Vector DB, Browser, K8s, Observability.



5. Build in phases, not in one shot.


6. Write tests, docs, and safe migrations for all changes.




---

1. Vision, Principles & Product Positioning

1.1 Product Vision

Build "Canada Immigration OS" — a multi-tenant SaaS platform for Canadian immigration consultants (RCICs and law firms) that:

Automates 70–80% of operational work:

Intake, eligibility, checklists, drafting, reminders, tracking, client comms.


Uses a multi-agent AI brain with:

Mastermind Consultant Agent (50-year expert)

Config Agent

Law Intelligence Agent

Eligibility/CRS Agent

CSA (Customer Success Agent)

Drafting & QA agents


Is self-feeding (learns from IRCC/PNP updates) and self-evolving (feature suggestions via Evolution Agent).

Keeps humans in ultimate control of legal rules and important product config.


1.2 Non-Negotiable Principles

1. Law Safety & Compliance First

No legal decision can bypass the Approved Rules Engine.

All law logic must be traceable to IRCC/official sources.



2. Human-in-the-loop for Rules & High-Risk Changes

Mastermind & Law Intelligence propose rules.

Human admins approve before rules go live.



3. Multi-Tenant Isolation & Data Safety

Strong org_id separation.

Regular backups and PITR.



4. Explainable AI

Every eligibility result must show:

Rules used

Inputs

Reasoning summary




5. API-First & Testable

Every feature accessible via API.

Automated tests, CI/CD, monitoring.




---

2. Actors & Roles

2.1 Human Roles

Platform SuperAdmin

Firm Owner / RCIC

Consultant

Paralegal / Staff

Client (Applicant)


2.2 AI / System Agents

1. Mastermind Consultant Agent – domain brain (50-year expert).


2. Config Agent – config & metadata manager (forms/fields/case types).


3. Law Intelligence Agent – IRCC/PNP scraper & rule extractor.


4. Eligibility & CRS Agent – applies Approved Rules Engine.


5. Drafting Agent – creates SOP, LOE, letters, submissions.


6. Document Intake Agent – OCR + metadata extraction + doc QC.


7. QA Agent – cross-check consistency across docs & data.


8. Checklist & Workflow Agent – task/checklist/flow creation & updates.


9. Calendar Agent – calendar sync & scheduling (Google/Outlook).


10. Customer Success Agent (CSA) – client success, communication, product Q&A.


11. Evolution Agent – self-evolution planner (features, performance, UX).


12. OpenHands Implementation Agent – codes, tests, deploys, fixes.



2.3 Tenancy & Isolation

Every entity (case, person, doc, template, config) must have org_id.

Platform-level data (e.g., IRCC law sources) are shared, but any firm-specific data remain isolated.



---

3. High-Level Architecture

3.1 Layers

1. Frontend Layer

Admin Console (platform-level)

Firm Console (owner/consultant/staff)

Client Portal (self-service portal)



2. Backend Services

Identity & Access Service

Org & User Management Service

Case & Person Service

Document Service (OCR & Metadata)

Workflow & Task Service

Template & Content Service

Calendar & Scheduling Service

Billing & Subscription Service

Analytics & Reporting Service

Law & Rule Engine Service

AI Orchestrator Service (for all agents)



3. Data Layer

PostgreSQL (primary DB)

S3-compatible Object Storage

Vector DB (Chroma/Qdrant/pgvector)

Logging & Metrics store



4. AI & MCP Layer

LLMs (Together AI + OpenAI, etc.)

MCP servers:

GitHub MCP

DB MCP

Vector DB MCP

Browser MCP (for IRCC sites & competitors)

K8s MCP

Observability MCP




5. DevOps Layer

GitHub Actions

Docker & Kubernetes

Monitoring (Prometheus + Grafana)

Error Tracking (Sentry)




---

4. Agent Specifications (All Agents, One Place)

4.1 Mastermind Consultant Agent

Role: Simulated 50-year Canada immigration consultant/lawyer.

Responsibilities:

Understand IRCC and PNP policies in depth (via Law Intelligence + RAG).

Design optimal workflows, forms, and case types with Config Agent.

Propose new rules in structured form.

Validate Evolution Agent suggestions for domain correctness.

Provide expert domain explanations for CSA & others.


Constraints:

Cannot directly modify rules, DB, or deploy code.

Can only propose rule changes for human approval.



---

4.2 Config Agent

Role: System configuration engineer.

Responsibilities:

Manage:

Case types

Forms & fields

Checklists

Templates

Feature flags


Implement Mastermind's configurations into DB via Config Service.

Apply changes via human-approved proposals where required.


Safety:

For legal-sensitive config (mapping to rules) → create proposals, not direct changes.



---

4.3 Law Intelligence Agent

Role: Law & policy ingestion pipeline.

Responsibilities:

Scrape official sources (IRCC, PNP, government bulletins).

Chunk & index content into vector DB.

Propose RuleProposal objects:

rule_id, category, conditions, effects, source_url.


Detect changes vs previous rule versions.


Tools:

Browser MCP (whitelist IRCC & gov domains).

Vector DB MCP for indexing/search.



---

4.4 Eligibility & CRS Agent

Role: Eligibility & scoring engine backed by approved rules.

Responsibilities:

Compute:

Eligibility for case types.

CRS scores, breakdowns, and what-if scenarios.


Generate explanations referencing rule IDs & sources.


Safety:

MUST use Rule Engine API and never infer law logic directly from raw text.



---

4.5 Drafting Agent

Role: Document drafting specialist.

Artifacts:

SOP (study permit, PR via Express Entry, etc.)

LOE (PoF, previous refusals, explanations)

Work experience letters

Cover letters to visa offices

Client communication drafts (where appropriate)


Inputs:

Client profile & case data

Document metadata

Firm templates & preferences


Process:

Start from appropriate template.

Fill structured variables.

Generate free-text sections.

Flag unclear parts for consultant editing.


Safety:

Drafts must be approved by consultants before sharing with client or IRCC.



---

4.6 Document Intake Agent

Role: Ingest, parse, and validate documents.

Responsibilities:

Run OCR on PDFs/images.

Extract structured data:

Names, dates, positions, salaries, NOC hints, etc.


Identify missing or inconsistent info.

Feed QA Agent and case record.



---

4.7 QA Agent

Role: Consistency & readiness checker.

Responsibilities:

Check:

Consistency across documents and declared data.

CRS-related data is accurate (dates, education, work).

Required docs per checklist completed.


Provide:

A "readiness score" per case.

A list of red flags.




---

4.8 Checklist & Workflow Agent

Role: Orchestrates tasks & workflows.

Responsibilities:

Generate checklists and tasks based on:

Case type

Approved rules

Config templates


Adjust tasks when:

Law changes impact the case.

Client data changes.




---

4.9 Calendar Agent

Role: Calendar & scheduling integration.

Responsibilities:

Manage:

Consultation appointments

Biometrics, medicals, deadlines, follow-up reminders


Sync events with:

Google Calendar

Outlook/Office 365




---

4.10 Customer Success Agent (CSA)

Role: End-to-end client & consultant success manager.

Responsibilities:

Client-side:

Explain process, steps, next actions.

Answer product questions.

Answer law questions using approved rules.

Send reminders and status updates.


Consultant-side:

Daily digest of case status.

Highlight risks, delays, and stuck items.



Channels:

Portal chat

Email templates

Notifications


Safety:

No "new law advice"; must use Approved Rules & Mastermind support.



---

4.11 Evolution Agent

Role: Self-evolution brain.

Responsibilities:

Monitor:

Metrics (conversion, delays, drop-offs).

Logs (error rates, performance).

Feedback / NPS.

Competitor features (via Browser MCP, in a compliant manner).


Produce:

docs/evolution/YYYY-MM-DD.md

GitHub issues for OpenHands.




---

4.12 OpenHands Implementation Agent

Role: Autonomous engineering executor.

Responsibilities:

Follow spec & docs.

Implement features in phases.

Maintain tests & CI.

Fix bugs.

Maintain infra.


Constraints:

Always run tests before merging.

Only deploy with passing CI.

Respect branch & PR policies.



---

5. Law & Rules System (Heart of Legal Safety)

5.1 Entities

law_sources

id, url, type, fetched_at, raw_html, text, hash.


law_chunks

id, law_source_id, chunk_index, text, embedding_vector, tags.


rule_proposals

id, proposed_by_agent, source_url, rule_json, summary, created_at, status.


approved_rules

id, rule_id, version, category, conditions_json, effects_json, source_url, approved_by_user_id, approved_at, is_active.


rule_versions

History of each rule.



5.2 Flow

1. Fetch IRCC & PNP pages via Browser MCP.


2. Chunk & embed into vector store.


3. Law Intelligence Agent runs:

"Extract structured rules" → creates rule_proposals.



4. Human Admin reviews & edits proposals in Admin Console:

Approve → approved_rules entry created.



5. Eligibility Agent & CRS Agent use Rule Engine API only.



5.3 Rule Engine API

POST /rules/eligibility/check

Input: { case_type, client_data_json }

Output: { eligible: bool, reasons: [...], rules_used: [rule_ids] }


POST /rules/crs/calculate

Input: normalized candidate profile.

Output: CRS score breakdown + rule references.




---

6. Config System (Case Types, Forms, Fields)

6.1 Entities

config_case_types

id, org_id?, code, label, description, is_active.


config_fields

id, org_id?, case_type_id, field_key, label, input_type, validation_json, is_required, order, help_text.


config_forms

id, org_id?, case_type_id, name, layout_json.


config_checklists

id, org_id?, case_type_id, name, items_json.


config_feature_flags

id, org_id?, flag_key, is_enabled, metadata_json.


config_change_proposals

Proposed changes requiring approval.



6.2 Config Agent Flow

1. Receive natural language instruction:

"Add boolean field has_canadian_experience to EXPRESS_ENTRY_FSW form after noc_code."



2. Parse to a concrete config operation.


3. Fetch current config via Config API.


4. Apply change:

Directly for safe UI-only changes.

As config_change_proposals for law-sensitive mappings.




---

7. Case Types, Forms & Workflows

Example Case Types (initial):

EXPRESS_ENTRY_FSW

EXPRESS_ENTRY_CEC

BC_PNP_TECH

STUDY_PERMIT

SPOUSAL_SPONSORSHIP_INLAND

SPOUSAL_SPONSORSHIP_OUTLAND


Each case type configured with:

Required fields

Forms (step-wise intake)

Checklists

Default workflows (states, tasks, deadlines)



---

8. Template Engine (Docs, Emails, Checklists)

8.1 Template Types

DOC_SOP

DOC_LOE

DOC_EMPLOYER_LETTER

DOC_REFUSAL_REPLY

EMAIL_WELCOME

EMAIL_DOC_REQUEST

EMAIL_REMINDER

EMAIL_STATUS

CONTRACT_SERVICE_AGREEMENT

CHECKLIST_TEMPLATE


8.2 Template Entity

templates

id, org_id, template_type, name, version, body_markdown, variables_json, is_active, created_at, created_by.



Templates used by:

Drafting Agent

CSA (communications)

Workflow Agent (checklists)



---

9. Document & OCR Engine

9.1 Entities

documents

id, org_id, case_id, person_id, doc_type, filename, storage_key, status, uploaded_by, created_at.


document_versions

id, document_id, version, storage_key, created_at.


document_metadata

document_id, key, value.



9.2 Pipeline

1. Client uploads via portal.


2. File stored in S3.


3. Document Intake Worker triggers:

OCR (Tesseract / AWS Textract).

Metadata extraction (names, dates, etc.).



4. Metadata saved.


5. QA + Eligibility agent use metadata.




---

10. Workflow & Checklist Engine

10.1 Entities

tasks

id, org_id, case_id, assigned_to_user_id?, assigned_to_role?, title, description, due_at, status, priority.


checklist_instances

id, case_id, config_checklist_id, items_json, status.



10.2 Flow

Checklist Agent instantiates checklist from config.

Tasks auto-generated from checklist items.

CSA handles client communication around those tasks.



---

11. Client Portal, Self-Service & E-Signature

11.1 Features

Secure login.

Dashboard:

Current stage, next step, overall progress.


Checklist view:

Pending, completed, overdue.


Document upload & view.

Status timeline.

FAQ & interactive chat (CSA-powered).

E-signature flow:

Agreements

Consent forms

IMM forms requiring signature.



11.2 E-Signature Integration

Support:

DocuSign / HelloSign / Adobe Sign via API.


Entities:

esign_requests(id, org_id, case_id, person_id, template_id, external_envelope_id, status, created_at)


CSA handles:

Sending signature requests.

Tracking completion.

Reminders.




---

12. Consultant/Firm Console & Calendar/CRM

12.1 Firm Console Screens

Dashboard

Case List & Case Detail

Calendar View (per consultant & firm-wide)

Templates & Config

Billing & Subscription

Analytics & Reports

Feedback & Support


12.2 CRM & Lead Management

leads(id, org_id, source, status, contact_info, notes)

CSA can:

Onboard leads.

Schedule consults (Calendar Agent).

Nurture via email sequences.




---

13. Billing & Subscription

Plan-based pricing:

Per consultant seat

Per active case


Entities:

subscriptions, invoices, payments.


Integration: Stripe (initial).

SaaS-level metrics for firm owners.



---

14. Analytics & Reporting

14.1 Firm-level KPIs

Approval rate by case type.

Average processing time per stage.

Bottleneck stages.

Revenue, ARPU, LTV.


14.2 System-level KPIs

Usage per feature, per agent.

NPS & satisfaction metrics.

Error rate trends.



---

15. Memory Architecture

15.1 Types of Memory

1. Session Memory (short-term chat).


2. Case Memory (per case history, actions).


3. Client Memory (preferences, communications).


4. Firm Memory (templates, tone, configs).


5. Domain Memory (law, rules, best practices).



15.2 Storage

Structured: Postgres (AI sessions, messages, action logs).

Unstructured: vector DB for semantic recall.


Agents must query memory via APIs, not raw DB dumps.


---

16. Data Model & DB Schema (Outline)

Key tables (not exhaustive):

users, orgs, org_memberships

persons, families, family_members

cases, case_events, case_notes

documents, document_versions, document_metadata

tasks, checklist_instances

templates

law_sources, law_chunks, rule_proposals, approved_rules, rule_versions

config_case_types, config_fields, config_forms, config_checklists, config_feature_flags, config_change_proposals

ai_sessions, ai_messages, ai_actions

calendar_integrations, events

leads, subscriptions, invoices, payments

audit_log


All with org_id and timestamps.


---

17. API Design

RESTful or GraphQL.

Auth via JWT/opaque tokens.

All APIs require org_id scoping.

AI Orchestrator interacts with backend via internal client libraries.



---

18. DevOps, CI/CD & MCP Servers

18.1 Environments

dev, staging, prod.


18.2 CI

GitHub Actions:

Backend: black, ruff, mypy, pytest.

Frontend: eslint, tsc, jest or playwright.



18.3 CD

Build Docker images.

Deploy to K8s.

Feature flags for rollout.


18.4 MCP Servers

GitHub MCP – create/update issues, PRs.

DB MCP – run migrations & safe queries.

VectorDB MCP – manage embeddings.

Browser MCP – IRCC & competitor research.

K8s MCP – deploy, rollback, inspect pods.

Observability MCP – query metrics & logs.



---

19. Security, Compliance & Audit

TLS everywhere.

Encryption at rest (DB & S3).

RBAC enforced at API.

Full audit logs for:

Config changes

Rule changes

AI decisions (who, what, when, why).


PII minimization in logs.

Clear disclaimers about AI support.



---

20. OpenHands Autopilot Protocol

20.1 Prompt Contract for OpenHands

Every task to OpenHands should include:

Context: reference to this spec (docs/master_spec.md).

Scope: exactly what to implement.

Constraints: tests, docs, style rules.

Acceptance Criteria: list of verifiable checks.


20.2 Example: Bootstrap Task

> Create monorepo structure, FastAPI backend, Next.js frontend, base CI, Docker, and docs/master_spec.md with this content.



20.3 Example: Implement Config Agent

> Implement Config Service DB & APIs, Config Agent, tests, docs per sections 6 & 4.2.



20.4 Self-Evolution Loop

1. Evolution Agent reads metrics, logs, feedback, competitor features.


2. Writes evolution docs & GitHub issues.


3. OpenHands implements features.


4. CI/CD deploys.


5. Agents use new capabilities.




---

This spec covers:

All agents (including Customer Success Agent).

Mastermind + Config + Law Intelligence interplay.

Self-evolving architecture.

Client portal + self-service + e-signature.

Calendar & CRM.

Templates, workflows, checklists.

Rule Engine & law safety.

DevOps, MCP, OpenHands usage.