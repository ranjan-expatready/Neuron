# Admin Config UI (Read-Only) – Milestone 3.2

> Frontend-only, read-only surface for domain configuration transparency. No editing; driven entirely by backend Admin Config API responses. Not legal advice.

## Purpose
- Provide admins and config agents a quick way to inspect the loaded domain configuration (CRS, language, work experience, proof of funds, program rules, arranged employment, biometrics/medicals, documents, forms).
- Reinforce config-first governance: UI only displays what backend returns; no IRCC constants in the frontend.

## Route
- `/admin/config` (optional `?section=<name>` to deep-link to a section).

## Behavior
- Fetches sections from `GET /api/v1/admin/config/sections`.
- Fetches selected section from `GET /api/v1/admin/config/{section}`.
- Shows:
  - Banner: “Read-only / law-sensitive / config-driven”.
  - Sidebar list of sections.
  - Main panel with summary (keys/entries) and pretty-printed JSON for the selected section.
- If the API is inaccessible (e.g., auth in dev), the UI falls back to a clearly labeled DEV mock sample so engineers can still verify layout.

## Limitations
- Read-only; no save or edit actions.
- Auth behavior follows existing API protection. If unauthorized in dev, mock sample is shown with a warning banner.
- Config hashes are not surfaced yet; add when the backend exposes them.

## How to use (dev)
1) Start backend and frontend normally.
2) Navigate to `/admin/config`.
3) Click a section in the sidebar to view its JSON snapshot.
4) Use `?section=language` (for example) to deep-link to a specific section.


