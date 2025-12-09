import uuid

from src.app.cases.lifecycle_service import CaseLifecycleError, CaseLifecycleService
from src.app.db.database import SessionLocal
from src.app.models.tenant import Tenant
from src.app.models.user import User


def _setup(db):
    tenant = Tenant(name=f"Tenant Lifecycle {uuid.uuid4()}")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    user = User(
        email="owner@example.com",
        full_name="Owner",
        hashed_password="hash",
        tenant_id=tenant.id,
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return tenant, user


def test_case_lifecycle_transitions():
    db = SessionLocal()
    try:
        tenant, user = _setup(db)
        service = CaseLifecycleService(db)

        record = service.create_case(
            profile={"foo": "bar"},
            tenant_id=tenant.id,
            user_id=user.id,
            source="test",
        )
        assert record.status == "draft"

        record = service.submit_case(record.id, user.id, tenant.id)
        assert record.status == "submitted"

        record = service.mark_in_review(record.id, user.id, tenant.id)
        assert record.status == "in_review"

        record = service.mark_complete(record.id, user.id, tenant.id)
        assert record.status == "complete"

        record = service.archive_case(record.id, user.id, tenant.id)
        assert record.status == "archived"
    finally:
        db.close()


def test_invalid_transition():
    db = SessionLocal()
    try:
        tenant, user = _setup(db)
        service = CaseLifecycleService(db)
        record = service.create_case(
            profile={},
            tenant_id=tenant.id,
            user_id=user.id,
            source="test",
        )
        # cannot go directly to complete from draft
        try:
            service.mark_complete(record.id, user.id, tenant.id)
            raised = False
        except CaseLifecycleError:
            raised = True
        assert raised is True
    finally:
        db.close()

