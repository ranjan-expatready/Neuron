# Case History, Audit & Snapshots (Phase 3.5)

## Overview

Phase 3.5 adds persistent storage for case evaluations produced by `/api/v1/cases/evaluate`. Each evaluation writes:

- **CaseRecord** — canonical current state for the evaluation run.
- **CaseSnapshot** — immutable versioned snapshot (monotonic `version` per `case_id`).
- **CaseEvent** — lightweight audit event (`EVALUATION_CREATED`).

Scope is **backend-only**, internal/testing. No auth is wired yet; user/tenant linkage lands in Phase 4.

## Data Model

- **CaseRecord** (`case_records`)
  - `id` (UUID PK), `created_at`, `updated_at`, `source`, `status` (defaults `evaluated`)
  - `profile` (input payload), `program_eligibility`, `crs_breakdown`, `required_artifacts`
  - `config_fingerprint` (config hashes used), optional `tenant_id`, `created_by`
  - Relationships: `snapshots`, `events`

- **CaseSnapshot** (`case_snapshots`)
  - `id` (UUID PK), `case_id` (FK → CaseRecord), `snapshot_at`, `source`
  - `version` (int, monotonic per `case_id`)
  - Same payload fields as CaseRecord; **immutable** after insert

- **CaseEvent** (`case_events`)
  - `id` (UUID PK), `case_id` (nullable FK), `event_type` (e.g., `EVALUATION_CREATED`)
  - `created_at`, `actor` (`system` for now), `metadata` (JSON)

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

## Phase 3.5 Limitations

- Internal/testing only; no auth, tenancy scoping, or user linkage yet.
- Write path limited to Case Evaluation API; no update/delete of history.
- Config/domain files remain the source of truth; stored fingerprints mirror the hashes used per evaluation.

## Future (Phase 4)

- User/tenant-scoped history and RBAC.
- Authenticated access to history endpoints.
- Cross-environment provenance, IP/device metadata, and export hooks for compliance.

