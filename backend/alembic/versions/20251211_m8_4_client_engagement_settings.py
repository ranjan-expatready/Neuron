"""M8.4 client engagement settings and auto_mode flag"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "20251211_m8_4_client_engagement_settings"
down_revision = "20251210_m8_agentic_platform"
branch_labels = None
depends_on = None


def _index_exists(bind, table_name: str, index_name: str) -> bool:
    inspector = inspect(bind)
    return any(idx.get("name") == index_name for idx in inspector.get_indexes(table_name))


def _safe_create_index(name: str, table: str, columns, unique: bool = False):
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else "postgresql"
    if dialect == "sqlite" and _index_exists(bind, table, name):
        return
    op.create_index(name, table, columns, unique=unique)


def _safe_drop_index(name: str, table: str):
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else "postgresql"
    if dialect == "sqlite" and not _index_exists(bind, table, name):
        return
    op.drop_index(name, table_name=table)


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else "postgresql"
    if dialect != "sqlite":
        op.alter_column("alembic_version", "version_num", type_=sa.String(length=64))

    op.create_table(
        "client_engagement_settings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("auto_intake_reminders_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "auto_missing_docs_reminders_enabled", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column("min_days_between_intake_reminders", sa.Integer(), nullable=False, server_default="7"),
        sa.Column("min_days_between_docs_reminders", sa.Integer(), nullable=False, server_default="7"),
        sa.Column("quiet_hours_start", sa.Integer(), nullable=True),
        sa.Column("quiet_hours_end", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    # SQLite compatibility for indexes: use separate, idempotent op
    _safe_create_index("ix_client_engagement_settings_tenant_id", "client_engagement_settings", ["tenant_id"])

    # Add auto_mode flag to agent_actions
    with op.batch_alter_table("agent_actions") as batch_op:
        batch_op.add_column(sa.Column("auto_mode", sa.Boolean(), nullable=False, server_default=sa.false()))
    _safe_create_index("ix_agent_actions_auto_mode", "agent_actions", ["auto_mode"])


def downgrade():
    _safe_drop_index("ix_agent_actions_auto_mode", "agent_actions")
    with op.batch_alter_table("agent_actions") as batch_op:
        batch_op.drop_column("auto_mode")
    _safe_drop_index("ix_client_engagement_settings_tenant_id", "client_engagement_settings")
    op.drop_table("client_engagement_settings")
