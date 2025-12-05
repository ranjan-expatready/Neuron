"""Database utilities for cross-database compatibility."""

import os
import uuid

from sqlalchemy import JSON, Column, String
from sqlalchemy.dialects.postgresql import JSONB, UUID


def get_id_column():
    """Get appropriate ID column type based on database."""
    if os.getenv("DATABASE_URL", "").startswith("sqlite"):
        return Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    else:
        return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def get_uuid_column(name, foreign_key=None, nullable=True):
    """Get appropriate UUID column type based on database."""
    if os.getenv("DATABASE_URL", "").startswith("sqlite"):
        if foreign_key:
            return Column(name, String(36), foreign_key, nullable=nullable)
        else:
            return Column(name, String(36), nullable=nullable)
    else:
        if foreign_key:
            return Column(name, UUID(as_uuid=True), foreign_key, nullable=nullable)
        else:
            return Column(name, UUID(as_uuid=True), nullable=nullable)


def get_json_column(name, default=None):
    """Get appropriate JSON column type based on database."""
    if os.getenv("DATABASE_URL", "").startswith("sqlite"):
        return Column(name, JSON, default=default or {})
    else:
        return Column(name, JSONB, default=default or {})
