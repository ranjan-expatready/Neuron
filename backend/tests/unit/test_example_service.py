"""
Example service unit test.

This demonstrates unit testing patterns for services.
"""


from src.app.utils.helpers import generate_id, hash_string, sanitize_filename, validate_email


class TestExampleService:
    """Example service tests."""

    def test_generate_id_format(self):
        """Test that generated IDs are in correct format."""
        id_value = generate_id()
        # UUID format: 8-4-4-4-12 hex characters
        parts = id_value.split("-")
        assert len(parts) == 5
        assert all(len(part) in [8, 4, 12] for part in parts)

    def test_hash_string_consistency(self):
        """Test that hashing is consistent."""
        value = "test_string"
        hash1 = hash_string(value)
        hash2 = hash_string(value)
        assert hash1 == hash2
        assert hash1 != value  # Hashed value should differ from original

    def test_validate_email_cases(self):
        """Test email validation with various cases."""
        # Valid emails
        assert validate_email("user@example.com") is True
        assert validate_email("user.name@example.co.uk") is True
        assert validate_email("user+tag@example.com") is True

        # Invalid emails
        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("") is False

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Safe filename
        assert sanitize_filename("safe_file.txt") == "safe_file.txt"

        # Unsafe characters
        unsafe = 'file<>:"/\\|?*.txt'
        sanitized = sanitize_filename(unsafe)
        assert "<" not in sanitized
        assert ">" not in sanitized
        assert ":" not in sanitized
        assert "/" not in sanitized
