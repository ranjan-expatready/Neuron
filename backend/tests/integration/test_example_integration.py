"""
Example integration test.

Integration tests verify interactions between components.
This example shows testing a service that uses database and other dependencies.
"""
import pytest
from sqlalchemy.orm import Session

from src.app.models.user import User
from src.app.services.auth import AuthService


@pytest.mark.integration
class TestAuthServiceIntegration:
    """Integration tests for AuthService with database."""

    def test_create_and_verify_password(self, db_session: Session):
        """Test password creation and verification flow."""
        # Create password hash
        password = "test_password_123"
        hashed = AuthService.get_password_hash(password)

        # Verify hash is different from original
        assert hashed != password
        assert len(hashed) > 0

        # Verify password
        assert AuthService.verify_password(password, hashed) is True
        assert AuthService.verify_password("wrong_password", hashed) is False

    def test_create_user_and_authenticate(self, db_session: Session):
        """Test complete user creation and authentication flow."""
        # Create user
        user_data = {
            "email": "integration_test@example.com",
            "password": "testpass123",
            "first_name": "Integration",
            "last_name": "Test",
        }

        hashed_password = AuthService.get_password_hash(user_data["password"])
        user = User(
            email=user_data["email"],
            encrypted_password=hashed_password,
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Verify user was created
        assert user.id is not None
        assert user.email == user_data["email"]

        # Verify password
        assert AuthService.verify_password(user_data["password"], user.encrypted_password) is True

        # Test authentication
        authenticated_user = AuthService.authenticate_user(
            db_session, user_data["email"], user_data["password"]
        )
        assert authenticated_user is not None
        assert authenticated_user.email == user_data["email"]

        # Test wrong password
        wrong_auth = AuthService.authenticate_user(db_session, user_data["email"], "wrong_password")
        assert wrong_auth is None
