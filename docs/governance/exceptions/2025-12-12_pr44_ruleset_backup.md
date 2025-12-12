# Ruleset Backup — 2025-12-12 (PR #44)

Source: captured via `gh api repos/ranjan-expatready/Neuron/rulesets/<id>` prior to temporary relaxation.

## integration/* ruleset (ID: 11070317 — "Protect integration branches")
- Target: branches matching `refs/heads/integration/**`
- Enforcement: active
- Required approvals: **1**
- Required status checks: `CI / all`
- Strict required status checks policy: **true** (up-to-date required)
- Merge methods allowed: merge, squash, rebase
- Other rules: non_fast_forward, deletion protection
- Bypass actors: none (current_user_can_bypass: never)
- Timestamps: created `2025-12-12T13:47:40.837+04:00`, updated `2025-12-12T13:47:40.884+04:00`

## main ruleset (ID: 11070322 — "Protect main")
- Target: branch `refs/heads/main`
- Enforcement: active
- Required approvals: **1**
- Required status checks: `CI / all`
- Strict required status checks policy: **true** (up-to-date required)
- Merge methods allowed: merge, squash, rebase
- Other rules: non_fast_forward, deletion protection
- Bypass actors: none (current_user_can_bypass: never)
- Timestamps: created `2025-12-12T13:47:51.835+04:00`, updated `2025-12-12T13:47:51.886+04:00`

