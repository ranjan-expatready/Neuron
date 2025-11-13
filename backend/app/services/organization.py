from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.organization import Organization, OrganizationMembership
from ..models.user import User
from ..schemas.organization import OrganizationCreate, OrganizationUpdate
from datetime import datetime
import uuid


class OrganizationService:
    @staticmethod
    def get_organization_by_id(db: Session, org_id: uuid.UUID) -> Optional[Organization]:
        return db.query(Organization).filter(
            Organization.id == org_id, 
            Organization.deleted_at.is_(None)
        ).first()

    @staticmethod
    def get_user_organization(db: Session, user_id: uuid.UUID) -> Optional[Organization]:
        membership = db.query(OrganizationMembership).filter(
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.status == 'active'
        ).first()
        
        if not membership:
            return None
            
        return OrganizationService.get_organization_by_id(db, membership.org_id)

    @staticmethod
    def create_organization(db: Session, org_data: OrganizationCreate, owner_id: uuid.UUID) -> Organization:
        # Create organization
        org = Organization(
            name=org_data.name,
            domain=org_data.domain,
            type=org_data.type
        )
        db.add(org)
        db.flush()  # Get the org ID

        # Create owner membership
        membership = OrganizationMembership(
            org_id=org.id,
            user_id=owner_id,
            role='owner',
            status='active',
            joined_at=datetime.utcnow()
        )
        db.add(membership)
        
        db.commit()
        db.refresh(org)
        return org

    @staticmethod
    def update_organization(db: Session, org_id: uuid.UUID, org_data: OrganizationUpdate) -> Optional[Organization]:
        org = OrganizationService.get_organization_by_id(db, org_id)
        if not org:
            return None

        update_data = org_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(org, field, value)

        org.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(org)
        return org

    @staticmethod
    def get_organization_members(db: Session, org_id: uuid.UUID) -> List[OrganizationMembership]:
        return db.query(OrganizationMembership).filter(
            OrganizationMembership.org_id == org_id,
            OrganizationMembership.status == 'active'
        ).all()

    @staticmethod
    def get_user_membership(db: Session, org_id: uuid.UUID, user_id: uuid.UUID) -> Optional[OrganizationMembership]:
        return db.query(OrganizationMembership).filter(
            OrganizationMembership.org_id == org_id,
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.status == 'active'
        ).first()

    @staticmethod
    def check_user_org_access(db: Session, user_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        """Check if user has access to the specified organization"""
        membership = OrganizationService.get_user_membership(db, org_id, user_id)
        return membership is not None