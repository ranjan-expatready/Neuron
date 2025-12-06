# UI Configuration Layer (DRAFT)

Purpose: central, config-first source for branding and high-level layout. No hard-coded theme or nav in frontend; a future ThemeProvider/Layout builder will read these YAMLs.

Scope:
- Token-level settings (colors, typography, spacing, radius) and top-level layout (nav sections, dashboard blocks).
- Not pixel-perfect CSS; intended to drive design systems and runtime theming.

Consumption:
- Frontend should load via a validated ConfigService/ThemeProvider, not ad hoc file reads.
- Admins/agents should be able to edit YAML (or a UI wrapper) without touching code.

Versioning:
- Each file has `meta.version` and `meta.status` (DRAFT). Future overlays (draft/staging/prod) can layer environment-specific values.

Files:
- `theme.yaml` – token definitions (colors, typography, spacing, radius).
- `layout.yaml` – navigation/header/dashboard sections and toggles.

Status: DRAFT – structure + examples only; tenant-specific themes/layouts will be managed via admin/config flows.
