"""
Simplified database model tests that work with SQLite.
"""
from datetime import datetime

import pytest
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Create a simple test base for SQLite compatibility
TestBase = declarative_base()


class SimpleUser(TestBase):
    __tablename__ = "simple_users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    encrypted_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)


class TestSimpleModels:
    """Test simplified models for SQLite compatibility."""

    @pytest.fixture
    def simple_db_session(self):
        """Create a simple SQLite session for testing."""
        engine = create_engine("sqlite:///:memory:")
        TestBase.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_create_simple_user(self, simple_db_session):
        """Test creating a simple user model."""
        user = SimpleUser(
            email="test@example.com",
            encrypted_password="hashed_password",
            first_name="Test",
            last_name="User",
        )

        simple_db_session.add(user)
        simple_db_session.commit()
        simple_db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.created_at is not None

    def test_user_email_unique_constraint(self, simple_db_session):
        """Test that user email must be unique."""
        user1 = SimpleUser(
            email="duplicate@example.com",
            encrypted_password="password1",
            first_name="User",
            last_name="One",
        )

        user2 = SimpleUser(
            email="duplicate@example.com",
            encrypted_password="password2",
            first_name="User",
            last_name="Two",
        )

        simple_db_session.add(user1)
        simple_db_session.commit()

        simple_db_session.add(user2)
        with pytest.raises(Exception):  # SQLite will raise IntegrityError
            simple_db_session.commit()

    def test_user_soft_delete(self, simple_db_session):
        """Test user soft delete functionality."""
        user = SimpleUser(
            email="delete@example.com",
            encrypted_password="password",
            first_name="Delete",
            last_name="Me",
        )

        simple_db_session.add(user)
        simple_db_session.commit()

        # Soft delete
        user.deleted_at = datetime.utcnow()
        simple_db_session.commit()

        assert user.deleted_at is not None

    def test_user_query_operations(self, simple_db_session):
        """Test basic query operations."""
        # Create multiple users
        users = [
            SimpleUser(
                email="user1@example.com",
                encrypted_password="pass1",
                first_name="User",
                last_name="One",
            ),
            SimpleUser(
                email="user2@example.com",
                encrypted_password="pass2",
                first_name="User",
                last_name="Two",
            ),
            SimpleUser(
                email="user3@example.com",
                encrypted_password="pass3",
                first_name="User",
                last_name="Three",
            ),
        ]

        for user in users:
            simple_db_session.add(user)
        simple_db_session.commit()

        # Test queries
        all_users = simple_db_session.query(SimpleUser).all()
        assert len(all_users) == 3

        user_by_email = (
            simple_db_session.query(SimpleUser)
            .filter(SimpleUser.email == "user2@example.com")
            .first()
        )
        assert user_by_email is not None
        assert user_by_email.first_name == "User"
        assert user_by_email.last_name == "Two"

        users_by_name = (
            simple_db_session.query(SimpleUser).filter(SimpleUser.first_name == "User").all()
        )
        assert len(users_by_name) == 3
