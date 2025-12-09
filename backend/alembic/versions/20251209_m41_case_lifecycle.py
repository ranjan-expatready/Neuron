"""m4.1 tenant/user and case lifecycle extensions

Revision ID: 20251209_m41_case_lifecycle
Revises: 20251209_case_history
Create Date: 2025-12-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251209_m41_case_lifecycle"
down_revision = "20251209_case_history"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    op.create_table(
        "tenants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tenants_name", "tenants", ["name"], unique=False)

    if not inspector.has_table("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("tenant_id", sa.String(length=36), nullable=True),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("full_name", sa.String(length=255), nullable=True),
            sa.Column("hashed_password", sa.String(length=255), nullable=True),
            sa.Column("role", sa.String(length=50), server_default="agent", nullable=False),
            sa.Column("encrypted_password", sa.String(length=255), nullable=True),
            sa.Column("first_name", sa.String(length=100), nullable=True),
            sa.Column("last_name", sa.String(length=100), nullable=True),
            sa.Column("phone", sa.String(length=20)),
            sa.Column("profile", sa.JSON(), default={}),
            sa.Column("preferences", sa.JSON(), default={}),
            sa.Column("professional_info", sa.JSON(), default={}),
            sa.Column("last_login_at", sa.DateTime(timezone=True)),
            sa.Column("email_verified_at", sa.DateTime(timezone=True)),
            sa.Column("phone_verified_at", sa.DateTime(timezone=True)),
            sa.Column("two_factor_enabled", sa.Boolean(), default=False),
            sa.Column("two_factor_secret", sa.String(length=255)),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("deleted_at", sa.DateTime(timezone=True)),
        )

    user_columns = {col["name"] for col in inspector.get_columns("users")}
    unique_constraints = {c.get("name") for c in inspector.get_unique_constraints("users")}
    indexes = {i.get("name") for i in inspector.get_indexes("users")}

    with op.batch_alter_table("users") as batch_op:
        if "tenant_id" not in user_columns:
            batch_op.add_column(sa.Column("tenant_id", sa.String(length=36), nullable=True))
        if "full_name" not in user_columns:
            batch_op.add_column(sa.Column("full_name", sa.String(length=255), nullable=True))
        if "hashed_password" not in user_columns:
            batch_op.add_column(sa.Column("hashed_password", sa.String(length=255), nullable=True))
        if "role" not in user_columns:
            batch_op.add_column(sa.Column("role", sa.String(length=50), server_default="agent", nullable=False))
        if "users_email_key" in unique_constraints:
            batch_op.drop_constraint("users_email_key", type_="unique")
        if "ix_users_email" in indexes:
            batch_op.drop_index("ix_users_email")
        if "tenant_id" in user_columns:
            batch_op.create_foreign_key("fk_users_tenant", "tenants", ["tenant_id"], ["id"], ondelete="CASCADE")
        batch_op.create_unique_constraint("uq_users_tenant_email", ["tenant_id", "email"])
        batch_op.create_index("ix_users_email", ["email"])

    with op.batch_alter_table("case_records") as batch_op:
        batch_op.add_column(sa.Column("tenant_id", sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column("created_by_user_id", sa.String(length=36), nullable=True))
        batch_op.alter_column("status", server_default="draft")
        batch_op.create_foreign_key("fk_case_records_tenant", "tenants", ["tenant_id"], ["id"], ondelete="CASCADE")
        batch_op.create_foreign_key("fk_case_records_user", "users", ["created_by_user_id"], ["id"], ondelete="SET NULL")

    with op.batch_alter_table("case_snapshots") as batch_op:
        batch_op.add_column(sa.Column("tenant_id", sa.String(length=36), nullable=True))
        batch_op.create_foreign_key("fk_case_snapshots_tenant", "tenants", ["tenant_id"], ["id"], ondelete="CASCADE")

    with op.batch_alter_table("case_events") as batch_op:
        batch_op.add_column(sa.Column("tenant_id", sa.String(length=36), nullable=True))
        batch_op.create_foreign_key("fk_case_events_tenant", "tenants", ["tenant_id"], ["id"], ondelete="CASCADE")


def downgrade():
    with op.batch_alter_table("case_events") as batch_op:
        batch_op.drop_constraint("fk_case_events_tenant", type_="foreignkey")
        batch_op.drop_column("tenant_id")

    with op.batch_alter_table("case_snapshots") as batch_op:
        batch_op.drop_constraint("fk_case_snapshots_tenant", type_="foreignkey")
        batch_op.drop_column("tenant_id")

    with op.batch_alter_table("case_records") as batch_op:
        batch_op.drop_constraint("fk_case_records_user", type_="foreignkey")
        batch_op.drop_constraint("fk_case_records_tenant", type_="foreignkey")
        batch_op.drop_column("created_by_user_id")
        batch_op.drop_column("tenant_id")
        batch_op.alter_column("status", server_default="evaluated")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("fk_users_tenant", type_="foreignkey")
        batch_op.drop_constraint("uq_users_tenant_email", type_="unique")
        batch_op.drop_index("ix_users_email")
        batch_op.drop_column("role")
        batch_op.drop_column("hashed_password")
        batch_op.drop_column("full_name")
        batch_op.drop_column("tenant_id")

    op.drop_index("ix_tenants_name", table_name="tenants")
    op.drop_table("tenants")

