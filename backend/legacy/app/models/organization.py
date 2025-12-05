import os
import uuid

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    # Use String for SQLite compatibility, UUID for PostgreSQL
    if os.getenv("DATABASE_URL", "").startswith("sqlite"):
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        settings = Column(JSON, default={})
        billing_info = Column(JSON, default={})
        branding = Column(JSON, default={})
        compliance_settings = Column(JSON, default={})
    else:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        settings = Column(JSON, default={})
        billing_info = Column(JSON, default={})
        branding = Column(JSON, default={})
        compliance_settings = Column(JSON, default={})

    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    domain = Column(String(255), unique=True, index=True)
    type = Column(
        String(50), nullable=False, default="law_firm"
    )  # law_firm, solo_practice, consultancy
    subscription_tier = Column(String(50), default="starter")
    subscription_status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    memberships = relationship("OrganizationMembership", back_populates="organization")
    persons = relationship("Person", back_populates="organization")
    cases = relationship("Case", back_populates="organization")
    documents = relationship("Document", back_populates="organization")

    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name}, type={self.type})>"


class OrganizationMembership(Base):
    __tablename__ = "org_memberships"

    # Use String for SQLite compatibility, UUID for PostgreSQL
    if os.getenv("DATABASE_URL", "").startswith("sqlite"):
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        org_id = Column(
            String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
        )
        user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
        invited_by = Column(String(36), ForeignKey("users.id"))
        permissions = Column(JSON, default={})
    else:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        org_id = Column(
            String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
        )
        user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
        invited_by = Column(String(36), ForeignKey("users.id"))
        permissions = Column(JSON, default={})

    role = Column(String(50), nullable=False)  # owner, admin, consultant, staff, paralegal
    status = Column(String(50), default="active")  # active, suspended, pending
    invited_at = Column(DateTime(timezone=True))
    joined_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])

    # Constraints
    __table_args__ = (UniqueConstraint("org_id", "user_id", name="unique_org_user_membership"),)

    def __repr__(self):
        return f"<OrganizationMembership(org_id={self.org_id}, user_id={self.user_id}, role={self.role})>"
