"""m4.2 pricing plans and case types"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251209_m42_pricing_case_types"
down_revision = "20251209_m41_case_lifecycle"
branch_labels = None
depends_on = None


def _has_column(inspector, table: str, column: str) -> bool:
    return column in {c["name"] for c in inspector.get_columns(table)}


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # Tenants plan code
    if not _has_column(inspector, "tenants", "plan_code"):
        with op.batch_alter_table("tenants") as batch:
            batch.add_column(
                sa.Column("plan_code", sa.String(length=64), nullable=True, server_default="starter")
            )
        op.execute("UPDATE tenants SET plan_code='starter' WHERE plan_code IS NULL")
        with op.batch_alter_table("tenants") as batch:
            batch.alter_column("plan_code", existing_type=sa.String(length=64), nullable=False)

    # CaseRecord case_type
    if not _has_column(inspector, "case_records", "case_type"):
        with op.batch_alter_table("case_records") as batch:
            batch.add_column(
                sa.Column(
                    "case_type",
                    sa.String(length=100),
                    nullable=True,
                    server_default="express_entry_basic",
                )
            )
        op.execute(
            "UPDATE case_records SET case_type='express_entry_basic' WHERE case_type IS NULL"
        )
        with op.batch_alter_table("case_records") as batch:
            batch.alter_column(
                "case_type",
                existing_type=sa.String(length=100),
                nullable=False,
                server_default="express_entry_basic",
            )

    # CaseSnapshot case_type
    if not _has_column(inspector, "case_snapshots", "case_type"):
        with op.batch_alter_table("case_snapshots") as batch:
            batch.add_column(
                sa.Column(
                    "case_type",
                    sa.String(length=100),
                    nullable=True,
                    server_default="express_entry_basic",
                )
            )
        op.execute(
            "UPDATE case_snapshots SET case_type='express_entry_basic' WHERE case_type IS NULL"
        )
        with op.batch_alter_table("case_snapshots") as batch:
            batch.alter_column(
                "case_type",
                existing_type=sa.String(length=100),
                nullable=False,
                server_default="express_entry_basic",
            )


def downgrade():
    with op.batch_alter_table("case_snapshots") as batch:
        if _has_column(inspect(op.get_bind()), "case_snapshots", "case_type"):
            batch.drop_column("case_type")

    with op.batch_alter_table("case_records") as batch:
        if _has_column(inspect(op.get_bind()), "case_records", "case_type"):
            batch.drop_column("case_type")

    with op.batch_alter_table("tenants") as batch:
        if _has_column(inspect(op.get_bind()), "tenants", "plan_code"):
            batch.drop_column("plan_code")

