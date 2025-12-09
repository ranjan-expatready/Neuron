"""add case history and audit tables

Revision ID: 20251209_case_history
Revises: 
Create Date: 2025-12-09
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251209_case_history"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "case_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="evaluated"),
        sa.Column("profile", sa.JSON(), nullable=False),
        sa.Column("program_eligibility", sa.JSON(), nullable=False),
        sa.Column("crs_breakdown", sa.JSON(), nullable=True),
        sa.Column("required_artifacts", sa.JSON(), nullable=True),
        sa.Column("config_fingerprint", sa.JSON(), nullable=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("created_by", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_case_records_source", "case_records", ["source"])
    op.create_index("ix_case_records_tenant_id", "case_records", ["tenant_id"])

    op.create_table(
        "case_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("snapshot_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("profile", sa.JSON(), nullable=False),
        sa.Column("program_eligibility", sa.JSON(), nullable=False),
        sa.Column("crs_breakdown", sa.JSON(), nullable=True),
        sa.Column("required_artifacts", sa.JSON(), nullable=True),
        sa.Column("config_fingerprint", sa.JSON(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["case_records.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_id", "version", name="uq_case_snapshots_case_version"),
    )
    op.create_index("ix_case_snapshots_case_id", "case_snapshots", ["case_id"])
    op.create_index("ix_case_snapshots_source", "case_snapshots", ["source"])

    op.create_table(
        "case_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("actor", sa.String(length=100), nullable=False, server_default="system"),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["case_id"], ["case_records.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_case_events_case_id", "case_events", ["case_id"])


def downgrade():
    op.drop_index("ix_case_events_case_id", table_name="case_events")
    op.drop_table("case_events")
    op.drop_index("ix_case_snapshots_source", table_name="case_snapshots")
    op.drop_index("ix_case_snapshots_case_id", table_name="case_snapshots")
    op.drop_table("case_snapshots")
    op.drop_index("ix_case_records_tenant_id", table_name="case_records")
    op.drop_index("ix_case_records_source", table_name="case_records")
    op.drop_table("case_records")

