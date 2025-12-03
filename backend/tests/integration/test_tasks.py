"""
Workflow & Task Service tests covering ATDD + contract behaviors.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from src.app.models.config import ConfigChecklist
from src.app.models.person import Person
from src.app.schemas.case import CaseCreate
from src.app.schemas.task import CaseTaskCreate
from src.app.services.case import CaseService


@pytest.fixture
def workflow_case(db_session, test_organization, test_user_with_org):
    """Create a person + case to attach tasks to."""
    person = Person(
        org_id=str(test_organization.id),
        first_name="Workflow",
        last_name="Tester",
        email="workflow@example.com",
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)

    case_payload = CaseCreate(
        primary_person_id=uuid.UUID(person.id),
        case_type="EXPRESS_ENTRY_FSW",
        title="Workflow Automation Case",
        description="Case for workflow testing",
    )
    case = CaseService.create_case(
        db_session, case_payload, str(test_organization.id), str(test_user_with_org.id)
    )
    db_session.refresh(case)
    return case


def test_create_manual_task_and_list(
    client,
    admin_headers,
    workflow_case,
):
    due_at = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    payload = {
        "case_id": workflow_case.id,
        "title": "Collect client passport",
        "description": "Request passport scans from client",
        "due_at": due_at,
        "priority": "high",
    }
    response = client.post("/api/v1/tasks", json=payload, headers=admin_headers)
    assert response.status_code == 201, response.text
    task = response.json()
    assert task["title"] == payload["title"]
    assert task["case_id"] == workflow_case.id
    assert task["reminder_at"] is not None

    list_response = client.get(f"/api/v1/tasks?case_id={workflow_case.id}", headers=admin_headers)
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["total"] >= 1
    assert any(t["title"] == payload["title"] for t in body["tasks"])


def test_dependency_enforcement_and_resolution(client, admin_headers, workflow_case):
    # Create blocking task A
    task_a = client.post(
        "/api/v1/tasks",
        json={
            "case_id": workflow_case.id,
            "title": "Gather employment letters",
        },
        headers=admin_headers,
    ).json()

    # Create dependent task B referencing A
    task_b_payload = CaseTaskCreate(
        case_id=uuid.UUID(workflow_case.id),
        title="File work experience evidence",
        dependencies=[uuid.UUID(task_a["id"])],
    )
    task_b = client.post(
        "/api/v1/tasks",
        json=task_b_payload.model_dump(mode="json"),
        headers=admin_headers,
    ).json()

    # Attempt to start B before A done -> conflict
    blocked_resp = client.patch(
        f"/api/v1/tasks/{task_b['id']}",
        json={"status": "in_progress"},
        headers=admin_headers,
    )
    assert blocked_resp.status_code == 409
    assert "blocked" in blocked_resp.json()["detail"].lower()

    # Complete task A
    complete_a = client.patch(
        f"/api/v1/tasks/{task_a['id']}",
        json={"status": "in_progress"},
        headers=admin_headers,
    )
    assert complete_a.status_code == 200
    done_a = client.patch(
        f"/api/v1/tasks/{task_a['id']}",
        json={"status": "done"},
        headers=admin_headers,
    )
    assert done_a.status_code == 200

    # Now B can transition
    unblock_resp = client.patch(
        f"/api/v1/tasks/{task_b['id']}",
        json={"status": "in_progress"},
        headers=admin_headers,
    )
    assert unblock_resp.status_code == 200
    assert unblock_resp.json()["status"] == "in_progress"


def test_sync_endpoint_creates_template_tasks(
    client,
    admin_headers,
    workflow_case,
    db_session,
):
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
    db_session.add_all([item_one, item_two])
    db_session.commit()

    sync_resp = client.post(
        f"/api/v1/cases/{workflow_case.id}/tasks/sync",
        headers=admin_headers,
    )
    assert sync_resp.status_code == 200
    assert sync_resp.json()["synced"] == 2

    list_resp = client.get(
        f"/api/v1/tasks?case_id={workflow_case.id}&source=template",
        headers=admin_headers,
    )
    assert list_resp.status_code == 200
    template_titles = {task["title"] for task in list_resp.json()["tasks"]}
    assert "Collect supporting documents" in template_titles
    assert "Validate forms" in template_titles


def test_task_activity_logging(client, admin_headers, workflow_case):
    task = client.post(
        "/api/v1/tasks",
        json={"case_id": workflow_case.id, "title": "Schedule client call"},
        headers=admin_headers,
    ).json()

    note_resp = client.post(
        f"/api/v1/tasks/{task['id']}/activities",
        json={"activity_type": "comment", "body": "Call scheduled for Friday"},
        headers=admin_headers,
    )
    assert note_resp.status_code == 201

    detail_resp = client.get(
        f"/api/v1/tasks/{task['id']}",
        headers=admin_headers,
    )
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["activities"] is not None
    assert any("Call scheduled" in (act["body"] or "") for act in detail["activities"])

    activities_resp = client.get(
        f"/api/v1/tasks/{task['id']}/activities",
        headers=admin_headers,
    )
    assert activities_resp.status_code == 200
    assert len(activities_resp.json()) >= 1
