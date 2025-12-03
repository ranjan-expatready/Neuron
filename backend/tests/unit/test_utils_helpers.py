"""
Unit tests for utility helper functions.

These tests demonstrate pure unit testing - no external dependencies.
"""
from datetime import datetime

import pytest

from src.app.utils.helpers import (
    format_datetime,
    generate_id,
    hash_string,
    parse_bool,
    safe_get,
    sanitize_filename,
    truncate_string,
    validate_email,
)


class TestGenerateID:
    """Test ID generation."""

    def test_generate_id_returns_string(self):
        """Test that generate_id returns a string."""
        result = generate_id()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_id_unique(self):
        """Test that generate_id produces unique IDs."""
        id1 = generate_id()
        id2 = generate_id()
        assert id1 != id2


class TestHashString:
    """Test string hashing."""

    def test_hash_string_sha256(self):
        """Test SHA256 hashing."""
        result = hash_string("test", algorithm="sha256")
        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 produces 64 hex characters

    def test_hash_string_md5(self):
        """Test MD5 hashing."""
        result = hash_string("test", algorithm="md5")
        assert isinstance(result, str)
        assert len(result) == 32  # MD5 produces 32 hex characters

    def test_hash_string_deterministic(self):
        """Test that hashing is deterministic."""
        result1 = hash_string("test")
        result2 = hash_string("test")
        assert result1 == result2

    def test_hash_string_invalid_algorithm(self):
        """Test that invalid algorithm raises error."""
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            hash_string("test", algorithm="invalid")


class TestFormatDatetime:
    """Test datetime formatting."""

    def test_format_datetime_default(self):
        """Test default datetime formatting."""
        dt = datetime(2025, 12, 2, 10, 30, 45)
        result = format_datetime(dt)
        assert result == "2025-12-02 10:30:45"

    def test_format_datetime_custom(self):
        """Test custom datetime formatting."""
        dt = datetime(2025, 12, 2, 10, 30, 45)
        result = format_datetime(dt, format_str="%Y/%m/%d")
        assert result == "2025/12/02"


class TestSafeGet:
    """Test safe dictionary access."""

    def test_safe_get_single_key(self):
        """Test safe_get with single key."""
        data = {"key": "value"}
        assert safe_get(data, "key") == "value"
        assert safe_get(data, "missing") is None
        assert safe_get(data, "missing", default="default") == "default"

    def test_safe_get_nested(self):
        """Test safe_get with nested keys."""
        data = {"level1": {"level2": {"level3": "value"}}}
        assert safe_get(data, "level1", "level2", "level3") == "value"
        assert safe_get(data, "level1", "level2", "missing") is None
        assert safe_get(data, "level1", "missing") is None

    def test_safe_get_invalid_path(self):
        """Test safe_get with invalid path."""
        data = {"key": "value"}
        assert safe_get(data, "key", "nested") is None


class TestTruncateString:
    """Test string truncation."""

    def test_truncate_string_short(self):
        """Test truncation of short string."""
        result = truncate_string("short", max_length=10)
        assert result == "short"

    def test_truncate_string_long(self):
        """Test truncation of long string."""
        long_string = "a" * 100
        result = truncate_string(long_string, max_length=50)
        assert len(result) == 50
        assert result.endswith("...")

    def test_truncate_string_custom_suffix(self):
        """Test truncation with custom suffix."""
        result = truncate_string("long string", max_length=5, suffix="…")
        assert result == "long…"


class TestSanitizeFilename:
    """Test filename sanitization."""

    def test_sanitize_filename_safe(self):
        """Test sanitization of safe filename."""
        assert sanitize_filename("safe_file.txt") == "safe_file.txt"

    def test_sanitize_filename_unsafe_chars(self):
        """Test sanitization removes unsafe characters."""
        result = sanitize_filename('file<>:"/\\|?*.txt')
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "/" not in result
        assert "\\" not in result

    def test_sanitize_filename_empty(self):
        """Test sanitization of empty filename."""
        result = sanitize_filename("")
        assert result == "file"


class TestValidateEmail:
    """Test email validation."""

    def test_validate_email_valid(self):
        """Test validation of valid emails."""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@domain.co.uk") is True

    def test_validate_email_invalid(self):
        """Test validation of invalid emails."""
        assert validate_email("invalid") is False
        assert validate_email("invalid@") is False
        assert validate_email("@domain.com") is False
        assert validate_email("test@") is False


class TestParseBool:
    """Test boolean parsing."""

    def test_parse_bool_true_values(self):
        """Test parsing of true values."""
        assert parse_bool(True) is True
        assert parse_bool("true") is True
        assert parse_bool("1") is True
        assert parse_bool("yes") is True
        assert parse_bool("on") is True

    def test_parse_bool_false_values(self):
        """Test parsing of false values."""
        assert parse_bool(False) is False
        assert parse_bool("false") is False
        assert parse_bool("0") is False
        assert parse_bool("no") is False
        assert parse_bool("off") is False

    def test_parse_bool_numeric(self):
        """Test parsing of numeric values."""
        assert parse_bool(1) is True
        assert parse_bool(0) is False
