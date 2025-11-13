from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..db.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, index=True)
    type = Column(String(50), nullable=False, default='law_firm')  # law_firm, solo_practice, consultancy
    settings = Column(JSONB, default={})
    subscription_tier = Column(String(50), default='starter')
    subscription_status = Column(String(50), default='active')
    billing_info = Column(JSONB, default={})
    branding = Column(JSONB, default={})
    compliance_settings = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    memberships = relationship("OrganizationMembership", back_populates="organization")
    persons = relationship("Person", back_populates="organization")
    cases = relationship("Case", back_populates="organization")

    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name}, type={self.type})>"


class OrganizationMembership(Base):
    __tablename__ = "org_memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # owner, admin, consultant, staff, paralegal
    permissions = Column(JSONB, default={})
    status = Column(String(50), default='active')  # active, suspended, pending
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    invited_at = Column(DateTime(timezone=True))
    joined_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])

    # Constraints
    __table_args__ = (
        UniqueConstraint('org_id', 'user_id', name='unique_org_user_membership'),
    )

    def __repr__(self):
        return f"<OrganizationMembership(org_id={self.org_id}, user_id={self.user_id}, role={self.role})>"