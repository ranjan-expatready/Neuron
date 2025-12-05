"""
Service layer tests.
"""
from datetime import timedelta

import pytest
from app.services.auth import AuthService


class TestAuthService:
    """Test the AuthService class methods."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "testpassword123"
        hashed = AuthService.get_password_hash(password)

        # Verify hash is different from original password
        assert hashed != password
        assert len(hashed) > 0

        # Verify password verification works
        assert AuthService.verify_password(password, hashed)
        assert not AuthService.verify_password("wrongpassword", hashed)

    def test_password_hashing_different_passwords(self):
        """Test that different passwords produce different hashes."""
        password1 = "password123"
        password2 = "password456"

        hash1 = AuthService.get_password_hash(password1)
        hash2 = AuthService.get_password_hash(password2)

        assert hash1 != hash2
        assert AuthService.verify_password(password1, hash1)
        assert AuthService.verify_password(password2, hash2)
        assert not AuthService.verify_password(password1, hash2)
        assert not AuthService.verify_password(password2, hash1)

    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = AuthService.create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0
        # JWT tokens have 3 parts separated by dots
        assert len(token.split(".")) == 3

    def test_create_access_token_with_expiry(self):
        """Test JWT token creation with custom expiry."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = AuthService.create_access_token(data, expires_delta)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self):
        """Test verification of valid JWT token."""
        data = {"sub": "test@example.com"}
        token = AuthService.create_access_token(data)

        class MockException(Exception):
            pass

        token_data = AuthService.verify_token(token, MockException)
        assert token_data.email == "test@example.com"

    def test_verify_token_invalid(self):
        """Test verification of invalid JWT token."""

        class MockException(Exception):
            pass

        with pytest.raises(MockException):
            AuthService.verify_token("invalid_token", MockException)

    def test_verify_token_expired(self):
        """Test verification of expired JWT token."""
        data = {"sub": "test@example.com"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = AuthService.create_access_token(data, expires_delta)

        class MockException(Exception):
            pass

        with pytest.raises(MockException):
            AuthService.verify_token(token, MockException)

    def test_verify_token_malformed(self):
        """Test verification of malformed JWT token."""

        class MockException(Exception):
            pass

        malformed_tokens = [
            "not.a.token",
            "too.few.parts",
            "too.many.parts.here.extra",
            "",
            "onlyonepart",
        ]

        for token in malformed_tokens:
            with pytest.raises(MockException):
                AuthService.verify_token(token, MockException)


class TestAuthServiceIntegration:
    """Integration tests for AuthService."""

    def test_full_auth_flow(self):
        """Test complete authentication flow."""
        # 1. Hash a password
        original_password = "mySecurePassword123!"
        hashed_password = AuthService.get_password_hash(original_password)

        # 2. Verify password
        assert AuthService.verify_password(original_password, hashed_password)

        # 3. Create token
        user_data = {"sub": "user@example.com", "user_id": "user123"}
        token = AuthService.create_access_token(user_data)

        # 4. Verify token
        class MockException(Exception):
            pass

        token_data = AuthService.verify_token(token, MockException)
        assert token_data.email == "user@example.com"

    def test_auth_flow_with_wrong_password(self):
        """Test authentication flow with wrong password."""
        original_password = "correctPassword"
        wrong_password = "wrongPassword"

        hashed_password = AuthService.get_password_hash(original_password)

        # Should fail with wrong password
        assert not AuthService.verify_password(wrong_password, hashed_password)

    def test_multiple_tokens_for_same_user(self):
        """Test creating multiple tokens for the same user."""
        import time

        user_data = {"sub": "user@example.com", "user_id": "user123"}

        token1 = AuthService.create_access_token(user_data)
        time.sleep(0.001)  # Small delay to ensure different timestamps
        token2 = AuthService.create_access_token(user_data)

        # Both tokens should be valid regardless of whether they're identical
        class MockException(Exception):
            pass

        token_data1 = AuthService.verify_token(token1, MockException)
        token_data2 = AuthService.verify_token(token2, MockException)

        assert token_data1.email == "user@example.com"
        assert token_data2.email == "user@example.com"


class TestAuthServiceEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_password_hash(self):
        """Test hashing empty password."""
        empty_password = ""
        hashed = AuthService.get_password_hash(empty_password)

        assert hashed != empty_password
        assert len(hashed) > 0
        assert AuthService.verify_password(empty_password, hashed)

    def test_very_long_password(self):
        """Test hashing very long password."""
        long_password = "a" * 1000  # 1000 character password
        hashed = AuthService.get_password_hash(long_password)

        assert hashed != long_password
        assert AuthService.verify_password(long_password, hashed)

    def test_special_characters_password(self):
        """Test password with special characters."""
        special_password = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        hashed = AuthService.get_password_hash(special_password)

        assert AuthService.verify_password(special_password, hashed)

    def test_unicode_password(self):
        """Test password with unicode characters."""
        unicode_password = "пароль123🔐"
        hashed = AuthService.get_password_hash(unicode_password)

        assert AuthService.verify_password(unicode_password, hashed)

    def test_token_with_empty_data(self):
        """Test creating token with empty data."""
        empty_data = {}
        token = AuthService.create_access_token(empty_data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_with_none_values(self):
        """Test creating token with None values."""
        data_with_none = {"sub": None, "user_id": None}
        token = AuthService.create_access_token(data_with_none)

        assert isinstance(token, str)
        assert len(token) > 0
