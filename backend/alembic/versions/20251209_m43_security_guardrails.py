"""m4.3 security guardrails: soft deletes"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251209_m43_security_guardrails"
down_revision = "20251209_m42_pricing_case_types"
branch_labels = None
depends_on = None


def _has_column(inspector, table: str, column: str) -> bool:
    return column in {c["name"] for c in inspector.get_columns(table)}


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    for table in ("case_records", "case_snapshots", "case_events"):
        if not _has_column(inspector, table, "is_deleted"):
            with op.batch_alter_table(table) as batch:
                batch.add_column(sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()))
        if not _has_column(inspector, table, "deleted_at"):
            with op.batch_alter_table(table) as batch:
                batch.add_column(sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    for table in ("case_events", "case_snapshots", "case_records"):
        with op.batch_alter_table(table) as batch:
            if _has_column(inspect(op.get_bind()), table, "deleted_at"):
                batch.drop_column("deleted_at")
            if _has_column(inspect(op.get_bind()), table, "is_deleted"):
                batch.drop_column("is_deleted")


