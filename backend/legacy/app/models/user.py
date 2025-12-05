import os
import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func

from ..db.database import Base


class User(Base):
    __tablename__ = "users"

    # Use String for SQLite compatibility, UUID for PostgreSQL
    if os.getenv("DATABASE_URL", "").startswith("sqlite"):
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        profile = Column(JSON, default={})
        preferences = Column(JSON, default={})
        professional_info = Column(JSON, default={})  # licenses, certifications, etc.
    else:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        profile = Column(JSON, default={})
        preferences = Column(JSON, default={})
        professional_info = Column(JSON, default={})  # licenses, certifications, etc.

    email = Column(String(255), unique=True, nullable=False, index=True)
    encrypted_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    last_login_at = Column(DateTime(timezone=True))
    email_verified_at = Column(DateTime(timezone=True))
    phone_verified_at = Column(DateTime(timezone=True))
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.first_name} {self.last_name})>"
