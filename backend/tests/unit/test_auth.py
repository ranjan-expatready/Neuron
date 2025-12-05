"""
Comprehensive tests for authentication service
Tests password hashing, verification, and edge cases
"""


from src.app.services.auth import AuthService


class TestPasswordHashing:
    """Test password hashing functionality"""

    def test_hash_normal_password(self):
        """Test hashing a normal length password"""
        password = "testpassword123"
        hashed = AuthService.get_password_hash(password)

        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt hash format

    def test_hash_short_password(self):
        """Test hashing a short password"""
        password = "short"
        hashed = AuthService.get_password_hash(password)

        assert hashed is not None
        assert hashed.startswith("$2b$")

    def test_hash_long_password(self):
        """Test hashing a password longer than 72 bytes (bcrypt limit)"""
        # Create a password longer than 72 bytes
        long_password = "a" * 100  # 100 characters = more than 72 bytes
        hashed = AuthService.get_password_hash(long_password)

        assert hashed is not None
        assert hashed.startswith("$2b$")

    def test_hash_very_long_password(self):
        """Test hashing a very long password"""
        very_long_password = "a" * 500  # 500 characters
        hashed = AuthService.get_password_hash(very_long_password)

        assert hashed is not None
        assert hashed.startswith("$2b$")

    def test_hash_special_characters(self):
        """Test hashing password with special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = AuthService.get_password_hash(password)

        assert hashed is not None
        assert hashed.startswith("$2b$")


class TestPasswordVerification:
    """Test password verification functionality"""

    def test_verify_correct_password(self):
        """Test verifying correct password"""
        password = "testpassword123"
        hashed = AuthService.get_password_hash(password)

        assert AuthService.verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Test verifying incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = AuthService.get_password_hash(password)

        assert AuthService.verify_password(wrong_password, hashed) is False

    def test_verify_long_password(self):
        """Test verifying long password (over 72 bytes)"""
        long_password = "a" * 100
        hashed = AuthService.get_password_hash(long_password)

        assert AuthService.verify_password(long_password, hashed) is True
        assert AuthService.verify_password("wrong", hashed) is False

    def test_verify_very_long_password(self):
        """Test verifying very long password"""
        very_long_password = "a" * 500
        hashed = AuthService.get_password_hash(very_long_password)

        assert AuthService.verify_password(very_long_password, hashed) is True

    def test_verify_special_characters(self):
        """Test verifying password with special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = AuthService.get_password_hash(password)

        assert AuthService.verify_password(password, hashed) is True
        assert AuthService.verify_password("wrong", hashed) is False

    def test_verify_unicode_password(self):
        """Test verifying password with unicode characters"""
        password = "测试密码123"
        hashed = AuthService.get_password_hash(password)

        assert AuthService.verify_password(password, hashed) is True
        assert AuthService.verify_password("wrong", hashed) is False


class TestPasswordEdgeCases:
    """Test edge cases for password handling"""

    def test_empty_password(self):
        """Test handling empty password"""
        password = ""
        hashed = AuthService.get_password_hash(password)

        assert hashed is not None
        assert AuthService.verify_password(password, hashed) is True

    def test_exactly_72_byte_password(self):
        """Test password exactly at bcrypt limit"""
        password = "a" * 72  # Exactly 72 bytes
        hashed = AuthService.get_password_hash(password)

        assert hashed is not None
        assert AuthService.verify_password(password, hashed) is True

    def test_73_byte_password(self):
        """Test password just over bcrypt limit"""
        password = "a" * 73  # 73 bytes, over limit
        hashed = AuthService.get_password_hash(password)

        assert hashed is not None
        assert AuthService.verify_password(password, hashed) is True

    def test_hash_consistency(self):
        """Test that same password produces different hashes (salt)"""
        password = "testpassword123"
        hash1 = AuthService.get_password_hash(password)
        hash2 = AuthService.get_password_hash(password)

        # Hashes should be different due to salt, but both should verify
        assert hash1 != hash2
        assert AuthService.verify_password(password, hash1) is True
        assert AuthService.verify_password(password, hash2) is True
