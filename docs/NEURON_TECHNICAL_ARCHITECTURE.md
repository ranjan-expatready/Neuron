# Neuron Technical Architecture

## 1) Layered Architecture
- **Presentation**: Next.js/React (admin, RCIC, client self-serve).
- **API layer**: FastAPI-style backend (routers, dependencies, RBAC).
- **Domain services**: Rule/CRS engines, eligibility, intake/document engines, case lifecycle, billing, agentic services.
- **Persistence**: PostgreSQL/SQLite with Alembic migrations; SQLAlchemy models.
- **Config + Domain Knowledge**: `config/domain/*.yaml`, `domain_knowledge/`.
- **Observability**: Structured logs, request IDs, `/internal/healthz`, `/internal/readyz`, metrics endpoints.

## 2) Backend Services Overview
- **Rule engine & CRS**: `CRSEngine`, explainability (structured + NL), case integration.
- **Eligibility**: Program eligibility driven by config; decision structures per program/plan.
- **Intake & Document**: Canonical profile API; field dictionary; intake templates; document matrix/checklist resolution.
- **Case lifecycle & history**: `CaseRecord`, `CaseSnapshot`, `CaseEvent` with audit trail.
- **Billing & plan enforcement**: Tenant plans/quotas; enforcement/usage tracking.
- **Security & tenant guardrails**: Auth, RBAC, tenant filters, soft deletes, security middleware.
- **Observability**: Logging/metrics as above; coverage targets enforced.

## 3) Frontend Architecture
- Next.js app structure with routes for admin, RCIC, client.
- Shared components: `IntakeFormRenderer`, checklist views, admin tables.
- Admin consoles: intake config (read/drafts/activation), agent activity, client engagement settings.
- RCIC views: case overview, intake, documents, agent engagement tab.
- Client self-serve: intake, document upload, status/reminders.

## 4) Config-first Domain Model
- `config/domain/*.yaml` drives CRS, eligibility programs/plans, intake templates, documents/forms, options.
- Guarantees: No hard-coded IRCC constants; config + domain knowledge are canonical; runtime loaders validate and enforce invariants.

## 5) Golden Tags & Releases
- Examples: `v0.5.0-phase5-golden`, `v0.8.3-phase8-agentic-shadow`.
- Each tag = known-good snapshot with passing tests, documented features, and recorded coverage.

