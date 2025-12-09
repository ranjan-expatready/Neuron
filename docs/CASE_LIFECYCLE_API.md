# Case Lifecycle API (Milestone 4.1)

## Overview

Tenant-aware lifecycle endpoints manage a case from draft through archive while recording immutable snapshots and audit events.

Statuses: `draft → submitted → in_review → complete → archived`.
Plan/feature gating (M4.2):
- Requires tenant plan feature `enable_case_lifecycle`.
- Case type must be allowed by the tenant plan; lifecycle operations enforce allowed case types and quotas on active cases.

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

- `Tenant`: id, name, metadata, plan_code, created_at/updated_at.
- `User`: id, email, full_name, hashed_password, role (`admin|agent|end_user`), tenant_id (unique per-tenant email).
- `CaseRecord`: carries `tenant_id`, `created_by_user_id`, lifecycle `status`, `case_type`.
- `CaseSnapshot` & `CaseEvent`: store `tenant_id`; snapshots also store `case_type` for audit isolation.

## Notes & Limitations

- Internal-only in 4.1; no auth middleware yet. Plan gating is enforced in 4.2.
- Tenant ownership is enforced per request by matching `tenant_id` on `CaseRecord`; plan gating can return 403/400 for disabled features or disallowed case types.
- Future phases will bind lifecycle endpoints to authenticated users/roles and surface plan selection/changes via billing.

