# Case Lifecycle API (Milestone 4.1)

## Overview

Tenant-aware lifecycle endpoints manage a case from draft through archive while recording immutable snapshots and audit events.

Statuses: `draft → submitted → in_review → complete → archived`.

Every transition writes:

- `CaseRecord.status` update (tenant-scoped)
- `CaseSnapshot` version (+1)
- `CaseEvent` with actor + metadata

### Security & RBAC (M4.3)
- Authentication required; user/tenant/role derived from the bearer token (no manual IDs in the request body).
- Tenant isolation: lifecycle actions are limited to the caller’s tenant; cross-tenant access raises `TenantAccessError`.
- Role-based transitions:
  - `draft → submitted`: owner, admin, case_manager
  - `submitted → in_review`: admin, case_manager
  - `in_review → complete`: admin
  - `complete → archived`: admin
  - `any → draft (reset)`: admin
- Soft deletes: soft-deleted cases are excluded by default; admins may pass `?include_deleted=true` to view.

## Endpoints (Phase 4.1)

Base: `/api/v1`

- `POST /case-lifecycle/{case_id}/submit`
- `POST /case-lifecycle/{case_id}/review`
- `POST /case-lifecycle/{case_id}/complete`
- `POST /case-lifecycle/{case_id}/archive`

Auth:
- Bearer token required; user, tenant, and role are resolved from the token.

Response:

```json
{
  "record": {
    "id": "...",
    "status": "in_review",
    "tenant_id": "...",
    "created_by_user_id": "...",
    "profile": { },
    "program_eligibility": { }
  },
  "last_snapshot_version": 2,
  "events": [
    {
      "id": "...",
      "event_type": "CASE_IN_REVIEW",
      "actor": "<user_id>",
      "metadata": {"from": "submitted", "to": "in_review"},
      "tenant_id": "..."
    }
  ]
}
```

## Models

- `Tenant`: id, name, metadata, created_at/updated_at.
- `User`: id, email, full_name, hashed_password, role (`admin|agent|end_user`), tenant_id (unique per-tenant email).
- `CaseRecord`: now carries `tenant_id`, `created_by_user_id`, lifecycle `status`.
- `CaseSnapshot` & `CaseEvent`: store `tenant_id` for audit isolation.

## Notes & Limitations

- Auth + tenant isolation are enforced in M4.3; cross-tenant access is blocked.
- RBAC applies per the matrix above; disallowed transitions return `LifecyclePermissionError`.
- Soft-deleted cases remain hidden unless an admin requests `include_deleted=true`.


> Security/Observability (M4.4): endpoints require authenticated users; logs carry request_id and tenant/user IDs; soft-deleted items stay hidden by default; internal health/metrics endpoints exist at /internal/healthz, /internal/readyz, /internal/metrics.
