from __future__ import annotations

from sqlalchemy.orm import Session


class RetentionService:
    """Stub retention service for future automated purging/archival."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def apply_retention_policies(self) -> None:
        """Placeholder: apply tenant-specific retention policies."""
        # Future: iterate tenant policies and soft-delete/purge eligible records.
        return

