"""m4.5 tenant billing state and plan tracking"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251210_m45_billing_plan_state"
down_revision = "20251209_m43_security_guardrails"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tenant_billing_state",
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("plan_code", sa.String(length=100), nullable=False, server_default="starter"),
        sa.Column("subscription_status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("renewal_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("usage_counters", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id"),
    )


def downgrade():
    op.drop_table("tenant_billing_state")

