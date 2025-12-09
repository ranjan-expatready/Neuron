"""Add workflow task tables

Revision ID: add_case_tasks
Revises: add_performance_indexes
Create Date: 2025-12-03
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_case_tasks"
down_revision = "add_performance_indexes"
branch_labels = None
depends_on = None


def upgrade():
    # Organization email column for legacy fixtures/tests
    op.add_column("organizations", sa.Column("email", sa.String(length=255), nullable=True))
    op.create_index("ix_organizations_email", "organizations", ["email"], unique=True)

    op.create_table(
        "case_tasks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("org_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("case_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="ready"),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="normal"),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="manual"),
        sa.Column("template_item_code", sa.String(length=100), nullable=True),
        sa.Column("assignee_id", sa.String(length=36), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reminder_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("blocked_reason", sa.String(length=255), nullable=True),
        sa.Column("task_metadata", sa.JSON(), nullable=True, server_default=sa.text("'{}'")),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_case_tasks_org_status", "case_tasks", ["org_id", "status"])
    op.create_index("idx_case_tasks_case_status", "case_tasks", ["case_id", "status"])
    op.create_index("idx_case_tasks_due_at", "case_tasks", ["org_id", "due_at"])

    op.create_table(
        "case_task_assignments",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("task_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="owner"),
        sa.Column("assignment_metadata", sa.JSON(), nullable=True, server_default=sa.text("'{}'")),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("unassigned_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["task_id"], ["case_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "case_task_activities",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("task_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("author_id", sa.String(length=36), nullable=True),
        sa.Column("activity_type", sa.String(length=50), nullable=False, server_default="comment"),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("activity_metadata", sa.JSON(), nullable=True, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["task_id"], ["case_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "case_task_dependencies",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("task_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("depends_on_task_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["task_id"], ["case_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["depends_on_task_id"], ["case_tasks.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("task_id", "depends_on_task_id", name="uq_case_task_dependency_pair"),
    )


def downgrade():
    op.drop_index("ix_organizations_email", table_name="organizations")
    op.drop_column("organizations", "email")

    op.drop_table("case_task_dependencies")
    op.drop_table("case_task_activities")
    op.drop_table("case_task_assignments")
    op.drop_index("idx_case_tasks_due_at", table_name="case_tasks")
    op.drop_index("idx_case_tasks_case_status", table_name="case_tasks")
    op.drop_index("idx_case_tasks_org_status", table_name="case_tasks")
    op.drop_table("case_tasks")
