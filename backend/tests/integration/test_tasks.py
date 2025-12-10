"""
Workflow & Task Service tests covering ATDD + contract behaviors.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from src.app.models.case import Case
from src.app.models.config import ConfigChecklist
from src.app.models.person import Person
from src.app.schemas.task import CaseTaskCreate


@pytest.fixture
def workflow_case(client):
    """Create a person + case to attach tasks to, using client's default org."""
    db = client.db_session
    person = Person(
        id=str(uuid.uuid4()),
        org_id=str(client.default_org.id),
        first_name="Workflow",
        last_name="Tester",
        email=f"workflow_{uuid.uuid4().hex[:6]}@example.com",
    )
    db.add(person)
    db.commit()
    db.refresh(person)

    case = Case(
        id=str(uuid.uuid4()),
        org_id=str(client.default_org.id),
        primary_person_id=person.id,
        case_number=f"CA-{uuid.uuid4().hex[:8].upper()}",
        case_type="EXPRESS_ENTRY_FSW",
        title="Workflow Automation Case",
        description="Case for workflow testing",
        status="draft",
        priority="normal",
        created_by=str(client.default_user.id),
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def test_create_manual_task_and_list(client, workflow_case):
    due_at = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    payload = {
        "case_id": workflow_case.id,
        "title": "Collect client passport",
        "description": "Request passport scans from client",
        "due_at": due_at,
        "priority": "high",
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 201, response.text
    task = response.json()
    assert task["title"] == payload["title"]
    assert task["case_id"] == workflow_case.id
    assert task["reminder_at"] is not None

    list_response = client.get(f"/api/v1/tasks?case_id={workflow_case.id}")
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["total"] >= 1
    assert any(t["title"] == payload["title"] for t in body["tasks"])


def test_dependency_enforcement_and_resolution(client, workflow_case):
    # Create blocking task A
    task_a_resp = client.post(
        "/api/v1/tasks",
        json={
            "case_id": workflow_case.id,
            "title": "Gather employment letters",
        },
    )
    assert task_a_resp.status_code == 201, task_a_resp.text
    task_a = task_a_resp.json()

    # Create dependent task B referencing A
    task_b_payload = CaseTaskCreate(
        case_id=uuid.UUID(workflow_case.id),
        title="File work experience evidence",
        dependencies=[uuid.UUID(task_a["id"])],
    )
    task_b_resp = client.post(
        "/api/v1/tasks",
        json=task_b_payload.model_dump(mode="json"),
    )
    assert task_b_resp.status_code == 201, task_b_resp.text
    task_b = task_b_resp.json()

    # Attempt to start B before A done -> conflict
    blocked_resp = client.patch(
        f"/api/v1/tasks/{task_b['id']}",
        json={"status": "in_progress"},
    )
    assert blocked_resp.status_code == 409
    assert "blocked" in blocked_resp.json()["detail"].lower()

    # Complete task A
    complete_a = client.patch(
        f"/api/v1/tasks/{task_a['id']}",
        json={"status": "in_progress"},
    )
    assert complete_a.status_code == 200
    done_a = client.patch(
        f"/api/v1/tasks/{task_a['id']}",
        json={"status": "done"},
    )
    assert done_a.status_code == 200

    # Now B can transition
    unblock_resp = client.patch(
        f"/api/v1/tasks/{task_b['id']}",
        json={"status": "in_progress"},
    )
    assert unblock_resp.status_code == 200
    assert unblock_resp.json()["status"] == "in_progress"


def test_sync_endpoint_creates_template_tasks(client, workflow_case):
    db = client.db_session
    item_one = ConfigChecklist(
        case_type_code="EXPRESS_ENTRY_FSW",
        item_code="DOC_COLLECTION",
        item_name="Collect supporting documents",
        description="Gather docs listed in template",
        sort_order=1,
        is_required=True,
        is_active=True,
    )
    item_two = ConfigChecklist(
        case_type_code="EXPRESS_ENTRY_FSW",
        item_code="FORM_VALIDATE",
        item_name="Validate forms",
        description="Ensure forms completed",
        sort_order=2,
        is_required=False,
        is_active=True,
    )
    db.add_all([item_one, item_two])
    db.commit()

    sync_resp = client.post(f"/api/v1/cases/{workflow_case.id}/tasks/sync")
    assert sync_resp.status_code == 200
    assert sync_resp.json()["synced"] == 2

    list_resp = client.get(f"/api/v1/tasks?case_id={workflow_case.id}&source=template")
    assert list_resp.status_code == 200
    template_titles = {task["title"] for task in list_resp.json()["tasks"]}
    assert "Collect supporting documents" in template_titles
    assert "Validate forms" in template_titles


def test_task_activity_logging(client, workflow_case):
    task_resp = client.post(
        "/api/v1/tasks",
        json={"case_id": workflow_case.id, "title": "Schedule client call"},
    )
    assert task_resp.status_code == 201, task_resp.text
    task = task_resp.json()

    note_resp = client.post(
        f"/api/v1/tasks/{task['id']}/activities",
        json={"activity_type": "comment", "body": "Call scheduled for Friday"},
    )
    assert note_resp.status_code == 201

    detail_resp = client.get(f"/api/v1/tasks/{task['id']}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["activities"] is not None
    assert any("Call scheduled" in (act["body"] or "") for act in detail["activities"])

    activities_resp = client.get(f"/api/v1/tasks/{task['id']}/activities")
    assert activities_resp.status_code == 200
    assert len(activities_resp.json()) >= 1
