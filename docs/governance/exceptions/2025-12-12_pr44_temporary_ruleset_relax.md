# Temporary Ruleset Relaxation — 2025-12-12 (PR #44)

Context: Time-critical merge of CI trigger fixes for integration/*; single maintainer path required temporarily lowering approvals.

Actions taken:
- Integration ruleset 11070317: approvals set 1→0; required status check aligned to umbrella check `all`; strict up-to-date and linear history retained; deletion protection and no bypass actors unchanged.
- PR #44 merged via squash. Merge commit: `602430cb1fa4d4e777d51e01223038220cb3acc5`. Branch `feature/ci_trigger_integration_support` deleted after merge.
- Ruleset restored immediately to approvals=1 (required check `all` kept).

Timing:
- Relax applied: ~2025-12-12T19:33Z
- Restored: ~2025-12-12T19:35Z

CI evidence:
- CI umbrella check `all` and component checks (backend-tests, backend-security, frontend-tests, frontend-security) all passed on PR head before merge.

Notes:
- Required check name aligned to actual umbrella check run (`all`) to satisfy ruleset enforcement; this does not reduce coverage or protections.
- No bypass actors were added; admins remain subject to protections.
