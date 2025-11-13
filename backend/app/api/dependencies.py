from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..services.auth import AuthService
from ..models.user import User
from ..models.organization import Organization
import uuid

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user"""
    token = credentials.credentials
    return AuthService.get_current_user(db, token)


def get_current_user_org(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Organization:
    """Get the current user's organization"""
    org = AuthService.get_user_organization(db, current_user)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any organization"
        )
    return org


def verify_org_access(org_id: str):
    """Dependency factory to verify user has access to specific organization"""
    def _verify_org_access(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> uuid.UUID:
        try:
            org_uuid = uuid.UUID(org_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid organization ID format"
            )
        
        if not AuthService.check_org_permission(db, current_user, org_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this organization"
            )
        return org_uuid
    
    return _verify_org_access