# Security & Tenant Guardrails (Milestone 4.3)

## Overview
- Purpose: Hardening multi-tenant security across all case APIs (evaluation, history, lifecycle, admin config).
- Scope delivered in M4.3: authenticated access, strict tenant isolation, lifecycle RBAC, soft deletes with retention stub, standardized security errors.

## Roles & RBAC
- Roles: `owner`, `admin`, `case_manager`, `viewer`.
- Lifecycle transition matrix:
  - `draft → submitted`: owner, admin, case_manager
  - `submitted → in_review`: admin, case_manager
  - `in_review → complete`: admin
  - `complete → archived`: admin
  - `any → draft (reset)`: admin
- Enforcement: lifecycle endpoints require auth; role is taken from the authenticated user; disallowed transitions raise `LifecyclePermissionError`.

## Tenant Isolation
- All case-related queries (CaseRecord, CaseSnapshot, CaseEvent) are scoped to `tenant_id == current_user.tenant_id`.
- Cross-tenant reads or lifecycle actions are blocked and return `TenantAccessError`.
- Admin config APIs are authenticated and tenant-aware; only admins/owners may access.

## Soft Deletes & Retention
- Fields added to case entities: `is_deleted: bool`, `deleted_at: datetime | null` on CaseRecord, CaseSnapshot, CaseEvent.
- Default behavior: soft-deleted records are excluded from lists/details/history; `?include_deleted=true` is admin-only.
- Retention: `RetentionService.apply_retention_policies()` stub exists for future purge of aged soft-deleted data (tenant-specific policies to be implemented later).

## Security Error Model
- `UnauthorizedError` — missing/invalid auth.
- `ForbiddenError` — authenticated but not allowed.
- `TenantAccessError` — tenant mismatch or cross-tenant attempt.
- `LifecyclePermissionError` — lifecycle transition not permitted for role.

## Invariants
- No cross-tenant access to cases, snapshots, or events.
- Lifecycle changes are tenant-scoped and audited (snapshots + events).
- Soft-deleted items stay hidden by default; only surfaced to admins with explicit include flag.
- Authentication is required on case evaluation, history, lifecycle, and admin config routes.

