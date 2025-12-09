"""Add performance indexes

Revision ID: add_performance_indexes
Revises:
Create Date: 2025-12-01

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_performance_indexes"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Case table indexes
    op.create_index("idx_cases_org_status", "cases", ["org_id", "status"], unique=False)
    op.create_index("idx_cases_org_type", "cases", ["org_id", "case_type"], unique=False)
    op.create_index("idx_cases_org_assigned", "cases", ["org_id", "assigned_to"], unique=False)
    op.create_index("idx_cases_org_created", "cases", ["org_id", "created_at"], unique=False)
    op.create_index("idx_cases_person", "cases", ["primary_person_id"], unique=False)
    op.create_index("idx_cases_status", "cases", ["status"], unique=False)

    # Document table indexes
    op.create_index(
        "idx_documents_org_status", "documents", ["org_id", "processing_status"], unique=False
    )
    op.create_index(
        "idx_documents_org_type", "documents", ["org_id", "document_type"], unique=False
    )
    op.create_index(
        "idx_documents_case_type", "documents", ["case_id", "document_type"], unique=False
    )
    op.create_index("idx_documents_uploaded", "documents", ["uploaded_at"], unique=False)
    op.create_index("idx_documents_ocr_status", "documents", ["ocr_status"], unique=False)

    # Person table indexes
    op.create_index("idx_persons_org_email", "persons", ["org_id", "email"], unique=False)
    op.create_index(
        "idx_persons_name_search", "persons", ["org_id", "first_name", "last_name"], unique=False
    )

    # User table indexes
    op.create_index("idx_users_org", "users", ["org_id"], unique=False)
    op.create_index("idx_users_deleted", "users", ["deleted_at"], unique=False)


def downgrade():
    # Drop indexes in reverse order
    op.drop_index("idx_users_deleted", table_name="users")
    op.drop_index("idx_users_org", table_name="users")
    op.drop_index("idx_persons_name_search", table_name="persons")
    op.drop_index("idx_persons_org_email", table_name="persons")
    op.drop_index("idx_documents_ocr_status", table_name="documents")
    op.drop_index("idx_documents_uploaded", table_name="documents")
    op.drop_index("idx_documents_case_type", table_name="documents")
    op.drop_index("idx_documents_org_type", table_name="documents")
    op.drop_index("idx_documents_org_status", table_name="documents")
    op.drop_index("idx_cases_status", table_name="cases")
    op.drop_index("idx_cases_person", table_name="cases")
    op.drop_index("idx_cases_org_created", table_name="cases")
    op.drop_index("idx_cases_org_assigned", table_name="cases")
    op.drop_index("idx_cases_org_type", table_name="cases")
    op.drop_index("idx_cases_org_status", table_name="cases")
