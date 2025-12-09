# Case Lifecycle API (Milestone 4.1)

## Overview

Tenant-aware lifecycle endpoints manage a case from draft through archive while recording immutable snapshots and audit events.

Statuses: `draft → submitted → in_review → complete → archived`.

Every transition writes:

- `CaseRecord.status` update (tenant-scoped)
- `CaseSnapshot` version (+1)
- `CaseEvent` with actor + metadata

## Endpoints (Phase 4.1)

Base: `/api/v1`

- `POST /case-lifecycle/{case_id}/submit`
- `POST /case-lifecycle/{case_id}/review`
- `POST /case-lifecycle/{case_id}/complete`
- `POST /case-lifecycle/{case_id}/archive`

Request body:

```json
{ "user_id": "<uuid>", "tenant_id": "<uuid>" }
```

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

- Internal-only in 4.1; no auth middleware yet.
- Tenant ownership is enforced per request by matching `tenant_id` on `CaseRecord`.
- Future phases will bind lifecycle endpoints to authenticated users/roles.

