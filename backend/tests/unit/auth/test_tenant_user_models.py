from sqlalchemy.exc import IntegrityError

from src.app.db.database import Base, SessionLocal, engine
from src.app.models.tenant import Tenant
from src.app.models.user import User


def test_tenant_and_user_unique_email_per_tenant():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        tenant = Tenant(name="Tenant A")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        user1 = User(
            email="agent@example.com",
            full_name="Agent One",
            hashed_password="hash",
            tenant_id=tenant.id,
            role="agent",
        )
        db.add(user1)
        db.commit()

        user2 = User(
            email="agent@example.com",
            full_name="Agent Two",
            hashed_password="hash2",
            tenant_id=tenant.id,
            role="agent",
        )
        db.add(user2)
        raised = False
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raised = True

        assert raised is True
    finally:
        db.close()

