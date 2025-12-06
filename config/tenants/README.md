# Tenant Configuration Layer (DRAFT)

Purpose: represent tenant-specific settings (modules, limits, theme/layout references) without hard-coding behavior in backend/src or frontend/src.

Scope:
- Enable/disable modules (EE/PNP/Study/Work/Family/Visitor/Humanitarian).
- Per-tenant limits (cases, users, storage).
- References to UI theme/layout configs.

Consumption:
- Future TenantConfigService should load/validate YAML, cache per tenant, and supply resolved config to services/UX. No ad hoc file reads.
- YAML remains the canonical source; DB overlays may follow, but must reconcile back to this schema.

Versioning:
- Each file carries `meta` with tenant code/name/status and references to UI configs.
- Mark status DRAFT/ACTIVE as appropriate; use overlays for staging/production later.

Files:
- `default.yaml` – baseline tenant configuration.
- `example_partner.yaml` – sample variant demonstrating module/limit/theme differences.

Status: DRAFT – examples only; replace with real tenant configs via admin workflows.
