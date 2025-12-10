# Billing & Plan Enforcement (M4.5)

## Overview
- Purpose: provide plan-aware feature gating and usage tracking without vendor lock-in.
- Scope: tenant-level plan state (`tenant_billing_state`), plan configuration (`config/plans.yaml`), BillingService abstraction, admin APIs, usage counters, and observability hooks.
- Status: M4.5 implemented as in-memory + DB stub (no external Stripe calls yet).

## Architecture
- **Config-first plans:** `config/plans.yaml` defines `default_plan` and per-plan `limits` (e.g., `max_cases`, `max_evaluations_per_month`, `express_entry_enabled`, `document_generation_enabled`).
- **Persistence:** `tenant_billing_state` stores `plan_code`, `subscription_status`, `renewal_date`, and `usage_counters` (per-event totals + monthly buckets).
- **Service:** `backend/src/app/services/billing_service.py`
  - `get_plan_status(tenant_id)` / `set_plan_status(...)`
  - `record_usage_event(tenant_id, event_name)`
  - `get_usage_snapshot(tenant_id)`
  - `apply_plan_limits(tenant_id, event_name)` raises `PlanLimitError` with `{error: "plan_limit_exceeded", detail: ...}` when exceeded.
- **Events tracked:** `case_created`, `evaluation_run`, `lifecycle_transition`, `document_generated` (stub).
- **Metrics/Logging:** `billing_events_total`, `plan_limit_violations_total`, structured logs (`component=billing`) for plan updates, usage increments, and violations.

## Enforcement Points
- Case creation API (`/api/v1/cases`): checks `max_cases`, records `case_created`.
- Case evaluation API (`/api/v1/cases/evaluate`): checks `express_entry_enabled` + `max_evaluations_per_month`, records `evaluation_run`.
- Case lifecycle API (`/api/v1/case-lifecycle/*`): checks `lifecycle_transitions_enabled`, records `lifecycle_transition`.
- Document generation: reserved hook; use `document_generated` event when generators are added.

## Admin Surface
- Router: `backend/src/app/api/routes/billing_admin.py`
  - `GET /api/v1/admin/billing/state` → plan state + limits.
  - `GET /api/v1/admin/billing/usage` → usage counters.
  - `POST /api/v1/admin/billing/update-plan` → change plan_code/status/renewal_date.
  - `GET /api/v1/admin/billing/portal-url` → stub URL placeholder.
- Access: admin/owner roles with tenant context (M4.3 RBAC).

## Migration
- Alembic revision `20251210_m45_billing_plan_state` adds `tenant_billing_state` table (FK tenants, primary key tenant_id).

## Testing
- New billing test suite under `backend/tests/billing/` covering state read/write, usage tracking, admin endpoints, and limit violations.
- Metrics test updated to assert new billing counters are exposed via `/internal/metrics`.

