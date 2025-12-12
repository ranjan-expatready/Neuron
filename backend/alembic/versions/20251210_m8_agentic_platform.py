"""m8.0 agentic platform skeleton: agent sessions/actions"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251210_m8_agentic_platform"
down_revision = "20251210_m45_billing_plan_state"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "agent_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=True),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("case_records.id", ondelete="SET NULL"), nullable=True),
        sa.Column("agent_name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_by_user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("context", sa.JSON(), nullable=True),
    )
    op.create_index("ix_agent_sessions_tenant_id", "agent_sessions", ["tenant_id"])
    op.create_index("ix_agent_sessions_agent_name", "agent_sessions", ["agent_name"])
    op.create_index("ix_agent_sessions_case_id", "agent_sessions", ["case_id"])

    op.create_table(
        "agent_actions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(length=36),
            sa.ForeignKey("agent_sessions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("tenant_id", sa.String(length=36), nullable=True),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("case_records.id", ondelete="SET NULL"), nullable=True),
        sa.Column("agent_name", sa.String(length=100), nullable=False),
        sa.Column("action_type", sa.String(length=100), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="suggested"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("error_message", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_agent_actions_tenant_case", "agent_actions", ["tenant_id", "case_id"])
    op.create_index("ix_agent_actions_agent_name", "agent_actions", ["agent_name"])
    op.create_index("ix_agent_actions_session_id", "agent_actions", ["session_id"])


def downgrade():
    op.drop_index("ix_agent_actions_session_id", table_name="agent_actions")
    op.drop_index("ix_agent_actions_agent_name", table_name="agent_actions")
    op.drop_index("ix_agent_actions_tenant_case", table_name="agent_actions")
    op.drop_table("agent_actions")

    op.drop_index("ix_agent_sessions_case_id", table_name="agent_sessions")
    op.drop_index("ix_agent_sessions_agent_name", table_name="agent_sessions")
    op.drop_index("ix_agent_sessions_tenant_id", table_name="agent_sessions")
    op.drop_table("agent_sessions")

