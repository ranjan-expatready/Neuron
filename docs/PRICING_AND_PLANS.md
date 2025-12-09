# Pricing & Plans (M4.2)

## Overview
Plan definitions are config-first and live in `config/plans.yaml`. Plans drive feature gating and quotas for tenants (case history, lifecycle, admin config, active case/user/storage limits) and define which case types a tenant can use.

## Plan Schema (`config/plans.yaml`)
- `plan_code`: unique string (e.g., `starter`, `pro`, `enterprise`)
- `features`: `enable_case_history`, `enable_case_lifecycle`, `enable_admin_config`
- `quotas`: `max_active_cases`, `max_users`, `max_storage_gb`
- `allowed_case_types`: list of case type codes allowed for this plan

Example:
```
plans:
  - plan_code: starter
    features:
      enable_case_history: true
      enable_case_lifecycle: false
      enable_admin_config: false
    quotas:
      max_active_cases: 5
      max_users: 5
      max_storage_gb: 5
    allowed_case_types:
      - express_entry_basic
```

## Runtime Enforcement
- Tenant has `plan_code` (default `starter`).
- Backend loads plans via `PlansConfigService`.
- Gating occurs in:
  - Case evaluation/history (`CaseHistoryService`) — checks feature, allowed case type, active case quota.
  - Case lifecycle (`CaseLifecycleService` and lifecycle API) — feature + allowed case type + quota.
  - Admin config API — requires `enable_admin_config`.
- Exceptions raise 403/400 with explanatory messages.

## Admin APIs
- `GET /api/v1/admin/plans?tenant_id=...` — returns plan catalog (requires admin_config feature on tenant plan).

## Frontend UX
- Dashboard shows current plan and quotas; features disabled by plan show “This feature requires Pro or higher.”
- Case history/lifecycle/admin config surfaces respect plan gating.

## Notes
- Plans are config-only; no billing processor integration in M4.2.
- Migrations add `plan_code` to `tenants` and default to `starter`.

