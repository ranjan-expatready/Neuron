import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.database import Base


class CaseTask(Base):
    __tablename__ = "case_tasks"
    __table_args__ = (
        Index("idx_case_tasks_org_status", "org_id", "status"),
        Index("idx_case_tasks_case_status", "case_id", "status"),
        Index("idx_case_tasks_due_at", "org_id", "due_at"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_id = Column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(
        String(32), nullable=False, default="ready"
    )  # ready, in_progress, blocked, done
    priority = Column(String(20), nullable=False, default="normal")  # low, normal, high, urgent
    source = Column(String(32), nullable=False, default="manual")  # manual, template, system
    template_item_code = Column(String(100))
    category = Column(String(100))
    assignee_id = Column(String(36), ForeignKey("users.id"))
    due_at = Column(DateTime(timezone=True))
    reminder_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    blocked_reason = Column(String(255))
    task_metadata = Column(JSON, default={})
    created_by = Column(String(36), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    case = relationship("Case", backref="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id])
    creator = relationship("User", foreign_keys=[created_by])
    activities = relationship(
        "CaseTaskActivity",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="CaseTaskActivity.created_at",
    )
    assignments = relationship(
        "CaseTaskAssignment", back_populates="task", cascade="all, delete-orphan"
    )
    dependency_links = relationship(
        "CaseTaskDependency",
        foreign_keys="CaseTaskDependency.task_id",
        back_populates="task",
        cascade="all, delete-orphan",
    )
    dependent_links = relationship(
        "CaseTaskDependency",
        foreign_keys="CaseTaskDependency.depends_on_task_id",
        back_populates="blocking_task",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<CaseTask(id={self.id}, case={self.case_id}, status={self.status}, title={self.title})>"


class CaseTaskAssignment(Base):
    __tablename__ = "case_task_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(
        String(36), ForeignKey("case_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    role = Column(String(50), default="owner")  # owner, collaborator, reviewer
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    unassigned_at = Column(DateTime(timezone=True))
    assignment_metadata = Column(JSON, default={})

    task = relationship("CaseTask", back_populates="assignments")
    user = relationship("User")

    def __repr__(self):
        return f"<CaseTaskAssignment(task={self.task_id}, user={self.user_id}, role={self.role})>"


class CaseTaskActivity(Base):
    __tablename__ = "case_task_activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(
        String(36), ForeignKey("case_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    activity_type = Column(
        String(50), default="comment"
    )  # comment, status_change, reminder, system
    body = Column(Text)
    activity_metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("CaseTask", back_populates="activities")
    author = relationship("User")

    def __repr__(self):
        return f"<CaseTaskActivity(task={self.task_id}, type={self.activity_type})>"


class CaseTaskDependency(Base):
    __tablename__ = "case_task_dependencies"
    __table_args__ = (
        UniqueConstraint("task_id", "depends_on_task_id", name="uq_case_task_dependency_pair"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(
        String(36), ForeignKey("case_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    depends_on_task_id = Column(
        String(36), ForeignKey("case_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship(
        "CaseTask",
        foreign_keys=[task_id],
        back_populates="dependency_links",
    )
    blocking_task = relationship(
        "CaseTask",
        foreign_keys=[depends_on_task_id],
        back_populates="dependent_links",
    )

    def __repr__(self):
        return f"<CaseTaskDependency(task={self.task_id}, depends_on={self.depends_on_task_id})>"
