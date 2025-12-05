"""
Security middleware for input validation and protection
"""
import logging
import re
from collections.abc import Callable
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """Security middleware for request validation"""

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|SCRIPT)\b)",
        r"(--|#|/\*|\*/)",
        r"(\bOR\b\s*\d+\s*=\s*\d+)",
        r"(\bAND\b\s*\d+\s*=\s*\d+)",
        r"('|(\\')|(;)|(\\)|(\%27)|(\%00))",
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e%5c",
    ]

    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """Check if value contains SQL injection patterns"""
        if not isinstance(value, str):
            return False

        value_upper = value.upper()
        for pattern in SecurityMiddleware.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {value[:50]}")
                return True
        return False

    @staticmethod
    def check_xss(value: str) -> bool:
        """Check if value contains XSS patterns"""
        if not isinstance(value, str):
            return False

        for pattern in SecurityMiddleware.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential XSS detected: {value[:50]}")
                return True
        return False

    @staticmethod
    def check_path_traversal(value: str) -> bool:
        """Check if value contains path traversal patterns"""
        if not isinstance(value, str):
            return False

        for pattern in SecurityMiddleware.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential path traversal detected: {value[:50]}")
                return True
        return False

    @staticmethod
    def validate_input(value: Any) -> tuple[bool, str]:
        """
        Validate input for security threats

        Returns:
            (is_valid, error_message)
        """
        if value is None:
            return True, ""

        # Convert to string for validation
        str_value = str(value)

        # Check SQL injection
        if SecurityMiddleware.check_sql_injection(str_value):
            return False, "Invalid input: potential SQL injection detected"

        # Check XSS
        if SecurityMiddleware.check_xss(str_value):
            return False, "Invalid input: potential XSS detected"

        # Check path traversal
        if SecurityMiddleware.check_path_traversal(str_value):
            return False, "Invalid input: potential path traversal detected"

        return True, ""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove path components
        filename = filename.replace("..", "").replace("/", "").replace("\\", "")

        # Remove null bytes
        filename = filename.replace("\x00", "")

        # Limit length
        if len(filename) > 255:
            filename = filename[:255]

        return filename

    @staticmethod
    def validate_file_upload(filename: str, content_type: str, file_size: int) -> tuple[bool, str]:
        """
        Validate file upload for security

        Returns:
            (is_valid, error_message)
        """
        # Validate filename
        is_valid, error = SecurityMiddleware.validate_input(filename)
        if not is_valid:
            return False, error

        # Sanitize filename
        filename = SecurityMiddleware.sanitize_filename(filename)

        # Check file size (50MB max)
        max_size = 50 * 1024 * 1024
        if file_size > max_size:
            return False, f"File size exceeds maximum allowed size of {max_size / (1024*1024)} MB"

        # Validate content type
        allowed_types = [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
        ]

        if content_type not in allowed_types:
            return False, f"File type {content_type} not allowed"

        return True, ""


async def security_middleware(request: Request, call_next: Callable):
    """
    Security middleware to validate requests

    Note: This is a basic implementation. For production, consider:
    - Rate limiting
    - Request size limits
    - More sophisticated validation
    - Security headers
    """
    # Skip validation for certain paths
    skip_paths = ["/docs", "/redoc", "/openapi.json", "/health"]
    if any(request.url.path.startswith(path) for path in skip_paths):
        return await call_next(request)

    # Validate query parameters
    for _, value in request.query_params.items():
        is_valid, error = SecurityMiddleware.validate_input(value)
        if not is_valid:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": error})

    # Validate path parameters
    for _, value in request.path_params.items():
        is_valid, error = SecurityMiddleware.validate_input(str(value))
        if not is_valid:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": error})

    # Wrap the next call in try-except to catch any errors
    try:
        response = await call_next(request)
    except ValueError as ve:
        error_msg = str(ve)
        # Catch password-related errors and return user-friendly message
        if "72 bytes" in error_msg or "longer than" in error_msg.lower():
            logger.warning(f"Password error caught in middleware: {error_msg}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": "Password processing error. Please try again or contact support."
                },
            )
        # Re-raise other ValueErrors
        raise
    except Exception as e:
        # Log unexpected errors but don't catch them
        logger.error(f"Unexpected error in security middleware: {type(e).__name__}: {e}")
        raise

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response
