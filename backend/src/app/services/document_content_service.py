import os
from typing import Optional

from src.app.models.document import Document


class DocumentContentService:
    """
    Pluggable content extraction for documents.
    Default: disabled via env OCR_ENABLED_FOR_DOC_REVIEWER. When disabled, returns None.
    When enabled, can be extended to use provider-specific OCR/PDF extraction.
    """

    def __init__(self, enabled: Optional[bool] = None, provider: Optional[str] = None, timeout_secs: Optional[int] = None):
        self.enabled = enabled if enabled is not None else os.getenv("OCR_ENABLED_FOR_DOC_REVIEWER", "false").lower() in (
            "1",
            "true",
            "yes",
        )
        self.provider = provider or os.getenv("OCR_PROVIDER", "stub")
        self.timeout_secs = timeout_secs or int(os.getenv("OCR_TIMEOUT_SECS", "10"))

    def extract_text(self, document: Document) -> Optional[str]:
        """
        Returns extracted text or None.
        Stub implementation: if disabled, None; if enabled and mime_type hints text/plain, return placeholder.
        Designed to be replaced or mocked in tests.
        """
        if not self.enabled:
            return None
        # Minimal non-failing behavior; real OCR/PDF parsing to be plugged in future milestones.
        if document.mime_type and document.mime_type.startswith("text/"):
            return "stub-text-content"
        return None


__all__ = ["DocumentContentService"]

