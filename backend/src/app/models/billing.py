from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.app.db.database import Base


class TenantBillingState(Base):
    """Billing state per tenant (plan + usage counters)."""

    __tablename__ = "tenant_billing_state"

    tenant_id = Column(
        String(36),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    plan_code = Column(String(100), nullable=False, default="starter")
    subscription_status = Column(String(50), nullable=False, default="active")
    renewal_date = Column(DateTime(timezone=True), nullable=True)
    usage_counters = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    tenant = relationship("Tenant", back_populates="billing_state")

    def __repr__(self) -> str:
        return (
            f"<TenantBillingState tenant_id={self.tenant_id} plan={self.plan_code} "
            f"status={self.subscription_status}>"
        )

