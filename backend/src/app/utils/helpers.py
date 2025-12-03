"""
Helper utility functions for common operations.
"""
import hashlib
from datetime import datetime
from typing import Any


def generate_id() -> str:
    """Generate a unique identifier."""
    import uuid

    return str(uuid.uuid4())


def hash_string(value: str, algorithm: str = "sha256") -> str:
    """Hash a string using the specified algorithm."""
    if algorithm == "sha256":
        return hashlib.sha256(value.encode("utf-8")).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(value.encode("utf-8")).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object as a string."""
    return dt.strftime(format_str)


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary values."""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result


def truncate_string(value: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate a string to a maximum length."""
    if len(value) <= max_length:
        return value
    return value[: max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to remove unsafe characters."""
    import re

    # Remove or replace unsafe characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")
    return sanitized or "file"


def validate_email(email: str) -> bool:
    """Validate email format."""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def parse_bool(value: Any) -> bool:
    """Parse a value to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return bool(value)
