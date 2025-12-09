# Case History, Audit & Snapshots (Phase 3.5)

## Overview

Phase 3.5 adds persistent storage for case evaluations produced by `/api/v1/cases/evaluate`. Phase 4.1/4.2 extend this with tenant/plan awareness (`tenant_id`, `plan_code`) and `case_type` enforcement. Each evaluation writes:

- **CaseRecord** — canonical current state for the evaluation run.
- **CaseSnapshot** — immutable versioned snapshot (monotonic `version` per `case_id`).
- **CaseEvent** — lightweight audit event (`EVALUATION_CREATED`).

Scope is **backend-only**, internal/testing. No auth is wired yet; user/tenant linkage lands in Phase 4.

## Data Model

- **CaseRecord** (`case_records`)
  - `id` (UUID PK), `created_at`, `updated_at`, `source`, `status` (defaults `evaluated`)
  - `profile` (input payload), `program_eligibility`, `crs_breakdown`, `required_artifacts`
  - `config_fingerprint` (config hashes used), `tenant_id`, `plan_code` via Tenant, `created_by`, `created_by_user_id`, `case_type`
  - Relationships: `snapshots`, `events`

- **CaseSnapshot** (`case_snapshots`)
  - `id` (UUID PK), `case_id` (FK → CaseRecord), `snapshot_at`, `source`
  - `version` (int, monotonic per `case_id`)
  - Same payload fields as CaseRecord plus `case_type`; **immutable** after insert

- **CaseEvent** (`case_events`)
  - `id` (UUID PK), `case_id` (nullable FK), `event_type` (e.g., `EVALUATION_CREATED`)
  - `created_at`, `actor` (`system` for now), `metadata` (JSON), `tenant_id`

## When Records Are Created

- POST `/api/v1/cases/evaluate`
  - Builds eligibility, CRS, and required artifacts (forms/documents).
  - Persists CaseRecord → CaseSnapshot (version +1 per case) → CaseEvent (`EVALUATION_CREATED`).
  - Response includes `case_id`, `version`, `audit.created_at`, and echoes computed payloads.

## APIs (Phase 3.5, Internal)

- **List recent cases**
  - `GET /api/v1/case-history`
  - Returns summaries: `id`, `created_at`, `source`, `status`, `programs`, `crs_total`.

- **Case detail with history**
  - `GET /api/v1/case-history/{case_id}`
  - Returns `record` (canonical state), `snapshots` (all versions), `events` (audit trail).

## Phase 4 Notes (M4.1/M4.2)

- Tenant-scoped history with `tenant_id`, `created_by_user_id`, and `case_type` persisted.
- Plan gating: history creation requires plan feature `enable_case_history`; active case quotas and allowed case types are enforced per plan.
- Access still internal/testing; full auth/RBAC remains future work.
- Write path limited to Case Evaluation API; no update/delete of history.
- Config/domain files remain the source of truth; stored fingerprints mirror the hashes used per evaluation.

