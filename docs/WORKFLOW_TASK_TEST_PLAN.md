## Workflow & Task Service – Comprehensive Test Plan

**Date:** December 3, 2025
**Authoring Agent:** TestSprite Agent (coordinated by Product Manager/CTO Agent)
**Goal:** Define the complete FAANG-style test strategy (ATDD + Contract + TDD + Property-Based) for the Workflow & Task Service prior to implementation.

---

### 1. Scope & Objectives

- Cover the full lifecycle of operational tasks tied to immigration cases:
  - Template-driven auto-generation on case creation
  - Manual task creation/editing
  - Assignment, reminders, status transitions, dependency handling
  - Multi-tenant isolation & audit trail
- Provide unambiguous acceptance tests and API contracts so the Backend API Agent can implement to spec and Frontend/TestSprite agents can validate consistently.

### 2. Assumptions & Dependencies

- Case, person, organization, and checklist data models already exist.
- Reminder delivery infrastructure can initially be mocked (focus on queue entries).
- Authentication & org scoping leverage existing JWT middleware.
- Feature flag `workflow_tasks_enabled` can gate rollout (default on for Phase 1 tenants).

---

### 3. Acceptance Tests (ATDD)

| ID      | Scenario               | Given                                   | When                                                             | Then                                                                                                     |
| ------- | ---------------------- | --------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| ATDD-01 | Case bootstrap tasks   | Org with case-type checklist template   | Consultant creates a new case                                    | Tasks auto-generate per template, ordered + due dates relative to case start, assigned per template role |
| ATDD-02 | Manual task creation   | Case exists with two staff members      | Paralegal creates manual task via API with assignee and due date | Task stored, audit entry created, reminder scheduled (T-24h)                                             |
| ATDD-03 | Task lifecycle         | Paralegal owns an `in_progress` task    | They complete task via PATCH                                     | Status = `done`, `completed_at` stored, reminders canceled, dependent tasks (if any) unlocked to `ready` |
| ATDD-04 | Dependency enforcement | Task B depends on Task A                | Staff attempts to start Task B before Task A complete            | API returns 409 with dependency error                                                                    |
| ATDD-05 | Reminder escalation    | Task due within 24h and still `blocked` | Reminder worker runs                                             | Escalation event recorded once; duplicate reminders prevented                                            |
| ATDD-06 | Multi-tenant isolation | Two orgs (A,B)                          | Org A user fetches tasks for Org B case ID                       | API returns 404 (or 403) enforcing tenancy                                                               |
| ATDD-07 | Checklist sync         | Template updated with new item          | Existing open cases opt to sync                                  | New tasks inserted with correct ordering without duplicating completed ones                              |
| ATDD-08 | Audit trail            | Task has prior comments                 | User adds new activity                                           | Activity appended with author + timestamp; list remains immutable                                        |

Each scenario will be backed by FastAPI integration tests once backend implementation is available.

---

### 4. API Contract Tests

All contracts validated via schemathesis / Pydantic models + JSON schema snapshots.

1. **POST `/api/v1/tasks`**

   - Request: `case_id`, `title`, `description`, `due_at`, `assignee_id`, `source` (`manual`|`template`), optional `dependencies`.
   - Response: `201 + TaskResponse` with `task_id`, `status`, `reminder_at`.
   - Error contracts: `400` (validation), `404` (case/assignee not found), `409` (dependency violation).

2. **GET `/api/v1/tasks`**

   - Query params: `case_id`, `status`, `assignee_id`, pagination.
   - Response: `200 + PaginatedTaskList` (includes `tasks`, `meta`).

3. **PATCH `/api/v1/tasks/{task_id}`**

   - Payload allows `status`, `assignee_id`, `due_at`, `metadata`.
   - Contracts for transition validation (`409` on illegal transitions, `412` on stale version).

4. **POST `/api/v1/tasks/{task_id}/activities`**

   - Adds audit comment / file reference.
   - Response `201 + ActivityResponse`.

5. **GET `/api/v1/tasks/{task_id}/activities`**

   - Returns chronological immutable history.

6. **POST `/api/v1/cases/{case_id}/tasks/sync`**
   - Triggers template sync; idempotent contract ensuring duplicates avoided.

Contract tests will assert response schemas, required fields, enum values (`status`, `source`, `priority`), and pagination metadata.

---

### 5. Property-Based Tests

1. **Dependency DAG validation**

   - Generate random DAGs (networkx) for task dependencies.
   - Property: Persisting tasks must reject graphs containing cycles; validation should always detect cycle before commit.

2. **Reminder scheduling**

   - Randomize `due_at` and SLA rules.
   - Property: `reminder_at` is always `due_at - SLA`, never in the past, and respects business hours flag (if enabled).

3. **Status transitions**

   - Fuzz transitions to ensure only allowed paths: `ready -> in_progress -> blocked -> in_progress -> done` etc.
   - Property: No transition bypasses `ready` state unless `auto_start` flag true.

4. **Multi-tenant isolation**
   - Randomly assign org IDs; property ensures queries filtered strictly by `org_id`.

---

### 6. Test Data & Fixtures

- Factory helpers for organizations, users (owner/admin/paralegal), cases, checklists, templates.
- Seed checklist template with 3 tasks (doc collection, form completion, review).
- Provide fixture for asynchronous reminder queue (mocked `ReminderQueue` interface) to assert enqueue/cancel calls.

---

### 7. Tooling & Coverage Targets

- **Backend:** pytest + FastAPI TestClient + hypothesis for property tests.
- **Contract:** schemathesis (OpenAPI-based) and snapshot testing via `pytest-approvaltests`.
- **Coverage:** raise backend coverage ≥80% with new module tests (lines + branches). Add `tests/workflow/` package.
- **CI:** extend backend workflow to run new suites and enforce coverage gate.

---

### 8. Next Steps

1. Backend API Agent uses this plan to design data model + services and implement endpoints (ASSIGN_007).
2. TestSprite Agent updates plan after backend implementation to include regression suites + integration with reminder scheduler.
3. Frontend Agent consumes the same contracts for UI work; E2E scenarios will reuse ATDD cases (task board, completion, reminders).

Deliverable stored at `docs/WORKFLOW_TASK_TEST_PLAN.md` for all agents. This satisfies the prerequisite for implementation per FAANG workflow.
