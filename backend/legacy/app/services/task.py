import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from ..models.case import Case
from ..models.config import ConfigChecklist
from ..models.task import CaseTask, CaseTaskActivity, CaseTaskAssignment, CaseTaskDependency
from ..schemas.task import CaseTaskActivityCreate, CaseTaskCreate, CaseTaskUpdate


class CaseTaskService:
    """Service layer for Workflow & Task operations."""

    VALID_STATUSES = ["ready", "in_progress", "blocked", "done", "cancelled"]
    STATUS_TRANSITIONS = {
        "ready": ["in_progress", "blocked", "cancelled"],
        "in_progress": ["blocked", "done", "cancelled"],
        "blocked": ["in_progress", "cancelled"],
        "done": [],
        "cancelled": [],
    }
    DEFAULT_REMINDER_HOURS = 24

    @staticmethod
    def list_tasks(
        db: Session,
        org_id: str,
        *,
        case_id: Optional[str] = None,
        status: Optional[str] = None,
        assignee_id: Optional[str] = None,
        source: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[CaseTask], int]:
        query = (
            db.query(CaseTask)
            .filter(CaseTask.org_id == org_id, CaseTask.deleted_at.is_(None))
            .order_by(CaseTask.due_at.is_(None), CaseTask.due_at, CaseTask.created_at)
        )

        if case_id:
            query = query.filter(CaseTask.case_id == case_id)
        if status:
            query = query.filter(CaseTask.status == status)
        if assignee_id:
            query = query.filter(CaseTask.assignee_id == assignee_id)
        if source:
            query = query.filter(CaseTask.source == source)
        if priority:
            query = query.filter(CaseTask.priority == priority)

        total = query.count()
        tasks = query.offset(skip).limit(limit).all()
        return tasks, total

    @staticmethod
    def get_task(db: Session, org_id: str, task_id: str) -> Optional[CaseTask]:
        return (
            db.query(CaseTask)
            .filter(
                CaseTask.id == task_id,
                CaseTask.org_id == org_id,
                CaseTask.deleted_at.is_(None),
            )
            .first()
        )

    @staticmethod
    def create_task(
        db: Session,
        org_id: str,
        created_by: str,
        payload: CaseTaskCreate,
    ) -> CaseTask:
        case = (
            db.query(Case)
            .filter(
                Case.id == str(payload.case_id),
                Case.org_id == org_id,
                Case.deleted_at.is_(None),
            )
            .first()
        )
        if not case:
            raise ValueError("Case not found or access denied")

        if payload.status and payload.status not in CaseTaskService.VALID_STATUSES:
            raise ValueError("Invalid task status")

        due_at = payload.due_at
        reminder_at = CaseTaskService._calculate_reminder(due_at)

        task = CaseTask(
            id=str(uuid.uuid4()),
            org_id=org_id,
            case_id=str(payload.case_id),
            title=payload.title,
            description=payload.description,
            priority=payload.priority or "normal",
            category=payload.category,
            status=payload.status or "ready",
            source=payload.source or "manual",
            assignee_id=str(payload.assignee_id) if payload.assignee_id else None,
            due_at=due_at,
            reminder_at=reminder_at,
            task_metadata=payload.metadata or {},
            created_by=created_by,
        )
        db.add(task)
        db.flush()

        if payload.assignee_id:
            CaseTaskService._record_assignment(
                db, task, str(payload.assignee_id), created_by, role="owner"
            )

        if payload.dependencies:
            CaseTaskService._replace_dependencies(
                db, task, [str(dep) for dep in payload.dependencies], org_id
            )

        CaseTaskService._record_activity(
            db,
            task,
            author_id=created_by,
            activity_type="created",
            body=f"Task created with status {task.status}",
        )

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task(
        db: Session,
        org_id: str,
        task_id: str,
        payload: CaseTaskUpdate,
        current_user_id: str,
    ) -> CaseTask:
        task = CaseTaskService.get_task(db, org_id, task_id)
        if not task:
            raise ValueError("Task not found")

        update_data = payload.model_dump(exclude_unset=True)
        status_before = task.status

        if "status" in update_data and update_data["status"]:
            new_status = update_data["status"]
            CaseTaskService._validate_status_transition(task.status, new_status)
            if new_status in ("in_progress", "done"):
                CaseTaskService._ensure_dependencies_complete(task)
            task.status = new_status
            if new_status == "done":
                task.completed_at = datetime.utcnow()
                task.reminder_at = None

        if "title" in update_data:
            task.title = update_data["title"]
        if "description" in update_data:
            task.description = update_data["description"]
        if "priority" in update_data:
            task.priority = update_data["priority"]
        if "category" in update_data:
            task.category = update_data["category"]
        if "blocked_reason" in update_data:
            task.blocked_reason = update_data["blocked_reason"]
        if "due_at" in update_data:
            task.due_at = update_data["due_at"]
            task.reminder_at = CaseTaskService._calculate_reminder(task.due_at)
        if "metadata" in update_data and update_data["metadata"] is not None:
            task.task_metadata = update_data["metadata"]

        if "assignee_id" in update_data:
            new_assignee = update_data["assignee_id"]
            if new_assignee:
                CaseTaskService._record_assignment(
                    db, task, str(new_assignee), current_user_id, role="owner"
                )
            else:
                CaseTaskService._close_active_assignment(db, task)
            task.assignee_id = str(new_assignee) if new_assignee else None

        if update_data.get("dependencies") is not None:
            CaseTaskService._replace_dependencies(
                db,
                task,
                [str(dep) for dep in update_data["dependencies"]],
                org_id,
            )

        task.updated_at = datetime.utcnow()
        db.add(task)

        if status_before != task.status:
            CaseTaskService._record_activity(
                db,
                task,
                author_id=current_user_id,
                activity_type="status_change",
                body=f"Status changed from {status_before} to {task.status}",
            )

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def add_activity(
        db: Session,
        org_id: str,
        task_id: str,
        payload: CaseTaskActivityCreate,
        author_id: str,
    ) -> CaseTaskActivity:
        task = CaseTaskService.get_task(db, org_id, task_id)
        if not task:
            raise ValueError("Task not found")

        activity = CaseTaskActivity(
            id=str(uuid.uuid4()),
            task_id=task.id,
            author_id=author_id,
            activity_type=payload.activity_type,
            body=payload.body,
            metadata=payload.metadata or {},
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def bootstrap_case_tasks(db: Session, case: Case) -> int:
        """Create template tasks for a new case."""
        checklist_items = (
            db.query(ConfigChecklist)
            .filter(
                ConfigChecklist.case_type_code == case.case_type,
                ConfigChecklist.is_active.is_(True),
            )
            .order_by(ConfigChecklist.sort_order)
            .all()
        )
        created = 0
        for item in checklist_items:
            exists = (
                db.query(CaseTask)
                .filter(
                    CaseTask.case_id == case.id,
                    CaseTask.template_item_code == item.item_code,
                    CaseTask.deleted_at.is_(None),
                )
                .first()
            )
            if exists:
                continue

            task = CaseTask(
                id=str(uuid.uuid4()),
                org_id=case.org_id,
                case_id=case.id,
                title=item.item_name,
                description=item.description,
                priority="high" if item.is_required else "normal",
                category=item.category,
                status="ready",
                source="template",
                template_item_code=item.item_code,
                task_metadata=item.checklist_metadata or {},
            )
            db.add(task)
            created += 1
        if created:
            db.commit()
        return created

    @staticmethod
    def sync_case_tasks(db: Session, case: Case) -> int:
        """Sync case tasks with the current checklist definition."""
        return CaseTaskService.bootstrap_case_tasks(db, case)

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_reminder(due_at: Optional[datetime]) -> Optional[datetime]:
        if not due_at:
            return None
        reminder = due_at - timedelta(hours=CaseTaskService.DEFAULT_REMINDER_HOURS)
        if due_at.tzinfo:
            now = datetime.now(tz=due_at.tzinfo)
        else:
            now = datetime.utcnow()
        if reminder <= now:
            return None
        return reminder

    @staticmethod
    def _validate_status_transition(current_status: str, new_status: str) -> None:
        if new_status not in CaseTaskService.VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")
        allowed = CaseTaskService.STATUS_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition from {current_status} to {new_status}. "
                f"Allowed transitions: {allowed}"
            )

    @staticmethod
    def _replace_dependencies(
        db: Session,
        task: CaseTask,
        dependency_ids: list[str],
        org_id: str,
    ) -> None:
        # Remove duplicates
        unique_ids = []
        for dep in dependency_ids:
            if dep not in unique_ids:
                unique_ids.append(dep)
        dependency_ids = unique_ids

        # Validate dependencies
        for dep_id in dependency_ids:
            if dep_id == task.id:
                raise ValueError("Task cannot depend on itself")
            blocking_task = CaseTaskService.get_task(db, org_id, dep_id)
            if not blocking_task or blocking_task.case_id != task.case_id:
                raise ValueError("Dependencies must belong to the same case")
            if CaseTaskService._creates_cycle(db, task.id, dep_id):
                raise ValueError("Dependency would create a cycle")

        # Clear existing dependencies
        db.query(CaseTaskDependency).filter(CaseTaskDependency.task_id == task.id).delete(
            synchronize_session=False
        )
        db.flush()

        for dep_id in dependency_ids:
            db.add(
                CaseTaskDependency(
                    id=str(uuid.uuid4()),
                    task_id=task.id,
                    depends_on_task_id=dep_id,
                )
            )

    @staticmethod
    def _ensure_dependencies_complete(task: CaseTask) -> None:
        for dep in task.dependency_links:
            if dep.blocking_task and dep.blocking_task.status != "done":
                raise ValueError(
                    f"Task blocked by {dep.blocking_task.title} ({dep.blocking_task.status})"
                )

    @staticmethod
    def _creates_cycle(db: Session, task_id: str, dependency_id: str) -> bool:
        """Detect if adding dependency would introduce a cycle."""
        stack = [dependency_id]
        visited = set()
        while stack:
            current = stack.pop()
            if current == task_id:
                return True
            if current in visited:
                continue
            visited.add(current)
            downstream = (
                db.query(CaseTaskDependency).filter(CaseTaskDependency.task_id == current).all()
            )
            stack.extend(dep.depends_on_task_id for dep in downstream)
        return False

    @staticmethod
    def _record_activity(
        db: Session,
        task: CaseTask,
        *,
        author_id: Optional[str],
        activity_type: str,
        body: Optional[str],
    ) -> None:
        activity = CaseTaskActivity(
            id=str(uuid.uuid4()),
            task_id=task.id,
            author_id=author_id,
            activity_type=activity_type,
            body=body,
            activity_metadata={},
        )
        db.add(activity)

    @staticmethod
    def _record_assignment(
        db: Session,
        task: CaseTask,
        user_id: str,
        assigned_by: str,
        role: str = "owner",
    ) -> None:
        CaseTaskService._close_active_assignment(db, task)
        assignment = CaseTaskAssignment(
            id=str(uuid.uuid4()),
            task_id=task.id,
            user_id=user_id,
            role=role,
            assignment_metadata={"assigned_by": assigned_by},
        )
        db.add(assignment)

    @staticmethod
    def _close_active_assignment(db: Session, task: CaseTask) -> None:
        active_assignment = (
            db.query(CaseTaskAssignment)
            .filter(
                CaseTaskAssignment.task_id == task.id,
                CaseTaskAssignment.unassigned_at.is_(None),
            )
            .order_by(CaseTaskAssignment.assigned_at.desc())
            .first()
        )
        if active_assignment:
            active_assignment.unassigned_at = datetime.utcnow()
            db.add(active_assignment)
