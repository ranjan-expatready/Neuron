"""
Input validators for API endpoints
"""
import re


def validate_uuid(value: str) -> str:
    """Validate UUID format"""
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    if not re.match(uuid_pattern, value, re.IGNORECASE):
        raise ValueError("Invalid UUID format")
    return value


def validate_email(email: str) -> str:
    """Validate email format"""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    return email


def validate_phone(phone: str) -> str:
    """Validate phone number format"""
    # Remove common formatting characters
    phone_clean = re.sub(r"[\s\-\(\)]", "", phone)
    # Check if it's a valid phone number (digits only, 10-15 digits)
    if not re.match(r"^\d{10,15}$", phone_clean):
        raise ValueError("Invalid phone number format")
    return phone_clean


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        return str(value)

    # Remove null bytes
    value = value.replace("\x00", "")

    # Trim whitespace
    value = value.strip()

    # Limit length
    if len(value) > max_length:
        value = value[:max_length]

    return value


def validate_case_status(status: str) -> str:
    """Validate case status"""
    valid_statuses = ["draft", "active", "submitted", "approved", "rejected", "closed"]
    if status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    return status


def validate_case_priority(priority: str) -> str:
    """Validate case priority"""
    valid_priorities = ["low", "normal", "high", "urgent"]
    if priority not in valid_priorities:
        raise ValueError(f"Invalid priority. Must be one of: {', '.join(valid_priorities)}")
    return priority


def validate_document_type(doc_type: str) -> str:
    """Validate document type"""
    valid_types = [
        "passport",
        "birth_certificate",
        "diploma",
        "transcript",
        "ielts",
        "celpip",
        "tef",
        "employment_letter",
        "pay_stub",
    ]
    if doc_type not in valid_types:
        raise ValueError(f"Invalid document type. Must be one of: {', '.join(valid_types)}")
    return doc_type
