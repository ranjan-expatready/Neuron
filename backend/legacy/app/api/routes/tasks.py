import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.organization import Organization
from ...models.user import User
from ...schemas.task import CaseTask as CaseTaskSchema
from ...schemas.task import CaseTaskActivity as CaseTaskActivitySchema
from ...schemas.task import (
    CaseTaskActivityCreate,
    CaseTaskCreate,
    CaseTaskListResponse,
    CaseTaskUpdate,
)
from ...services.task import CaseTaskService
from ..dependencies import get_current_user, get_current_user_org

router = APIRouter()


def _task_to_schema(task, *, include_activities: bool) -> CaseTaskSchema:
    dependencies = [dep.depends_on_task_id for dep in task.dependency_links]
    activities = (
        [_activity_to_schema(activity) for activity in task.activities]
        if include_activities and task.activities
        else None
    )
    payload = {
        "id": task.id,
        "org_id": task.org_id,
        "case_id": task.case_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "category": task.category,
        "source": task.source,
        "template_item_code": task.template_item_code,
        "assignee_id": task.assignee_id,
        "due_at": task.due_at,
        "reminder_at": task.reminder_at,
        "completed_at": task.completed_at,
        "blocked_reason": task.blocked_reason,
        "metadata": task.task_metadata or {},
        "created_by": task.created_by,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "dependencies": dependencies,
        "activities": activities,
    }
    return CaseTaskSchema(**payload)


def _activity_to_schema(activity) -> CaseTaskActivitySchema:
    payload = {
        "id": activity.id,
        "task_id": activity.task_id,
        "author_id": activity.author_id,
        "activity_type": activity.activity_type,
        "body": activity.body,
        "metadata": activity.activity_metadata or {},
        "created_at": activity.created_at,
    }
    return CaseTaskActivitySchema(**payload)


def _raise_from_value_error(error: ValueError) -> None:
    detail = str(error)
    lowered = detail.lower()
    status_code = status.HTTP_400_BAD_REQUEST
    conflict_tokens = ["dependency", "blocked", "cycle", "duplicate"]
    if any(token in lowered for token in conflict_tokens):
        status_code = status.HTTP_409_CONFLICT
    raise HTTPException(status_code=status_code, detail=detail)


@router.get("/", response_model=CaseTaskListResponse)
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    case_id: Optional[uuid.UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    assignee_id: Optional[uuid.UUID] = Query(None),
    source: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    tasks, total = CaseTaskService.list_tasks(
        db,
        str(current_org.id),
        case_id=str(case_id) if case_id else None,
        status=status_filter,
        assignee_id=str(assignee_id) if assignee_id else None,
        source=source,
        priority=priority,
        skip=skip,
        limit=limit,
    )
    return CaseTaskListResponse(
        tasks=[_task_to_schema(task, include_activities=False) for task in tasks],
        total=total,
    )


@router.post("/", response_model=CaseTaskSchema, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: CaseTaskCreate,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    try:
        task = CaseTaskService.create_task(db, str(current_org.id), str(current_user.id), payload)
        return _task_to_schema(task, include_activities=True)
    except ValueError as exc:
        _raise_from_value_error(exc)


@router.get("/{task_id}", response_model=CaseTaskSchema)
async def get_task(
    task_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    task = CaseTaskService.get_task(db, str(current_org.id), str(task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return _task_to_schema(task, include_activities=True)


@router.patch("/{task_id}", response_model=CaseTaskSchema)
async def update_task(
    task_id: uuid.UUID,
    payload: CaseTaskUpdate,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    try:
        task = CaseTaskService.update_task(
            db,
            str(current_org.id),
            str(task_id),
            payload,
            str(current_user.id),
        )
        return _task_to_schema(task, include_activities=True)
    except ValueError as exc:
        _raise_from_value_error(exc)


@router.post(
    "/{task_id}/activities",
    response_model=CaseTaskActivitySchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_activity(
    task_id: uuid.UUID,
    payload: CaseTaskActivityCreate,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    try:
        activity = CaseTaskService.add_activity(
            db,
            str(current_org.id),
            str(task_id),
            payload,
            str(current_user.id),
        )
        return _activity_to_schema(activity)
    except ValueError as exc:
        _raise_from_value_error(exc)


@router.get("/{task_id}/activities", response_model=list[CaseTaskActivitySchema])
async def list_task_activities(
    task_id: uuid.UUID,
    current_org: Organization = Depends(get_current_user_org),
    db: Session = Depends(get_db),
):
    task = CaseTaskService.get_task(db, str(current_org.id), str(task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return [_activity_to_schema(activity) for activity in task.activities]
