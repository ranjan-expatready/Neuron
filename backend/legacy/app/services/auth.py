import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from dotenv import load_dotenv
from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..models.organization import Organization, OrganizationMembership
from ..models.user import User
from ..schemas.auth import TokenData

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Use bcrypt directly instead of passlib to avoid wrap bug detection issues
# that can cause errors in certain server configurations
# We always pre-hash with SHA256 to ensure consistent length (< 72 bytes)


class AuthService:
    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        Since we always pre-hash with SHA256 before bcrypt, we need to do the same for verification.
        """
        # Pre-hash with SHA256 to match our hashing strategy
        password_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()

        # Use bcrypt directly to match our hashing approach
        # This avoids passlib's wrap bug detection issues
        try:
            return bcrypt.checkpw(password_hash.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception as e:
            # Log error but don't fail - this should never happen with proper hashes
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Password verification error (unexpected): {e}")
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Hash password using bcrypt.
        Bcrypt has a 72-byte limit, so we always pre-hash with SHA256 first
        to ensure consistent length and avoid any length-related issues.
        This approach is secure and handles all password lengths uniformly.

        NOTE: We use bcrypt directly instead of passlib to avoid wrap bug detection issues
        that can cause errors in certain server configurations.
        """
        # Always pre-hash with SHA256 to get fixed 64-char hex string (32 bytes)
        # This ensures we never hit the 72-byte limit and provides consistent handling
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

        # Use bcrypt directly to avoid passlib's wrap bug detection issues
        # This is more reliable and avoids the "72 bytes" error that can occur
        # with passlib in certain server configurations
        import bcrypt

        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password_hash.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str, credentials_exception) -> TokenData:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception
        return token_data

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.encrypted_password):
            return None
        return user

    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token_data = AuthService.verify_token(token, credentials_exception)
        user = (
            db.query(User).filter(User.email == token_data.email, User.deleted_at.is_(None)).first()
        )
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    def get_user_organization(db: Session, user: User) -> Optional[Organization]:
        membership = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.user_id == user.id, OrganizationMembership.status == "active"
            )
            .first()
        )

        if not membership:
            return None

        return (
            db.query(Organization)
            .filter(Organization.id == membership.org_id, Organization.deleted_at.is_(None))
            .first()
        )

    @staticmethod
    def check_org_permission(db: Session, user: User, required_org_id: str) -> bool:
        """Check if user has access to the specified organization"""
        user_org = AuthService.get_user_organization(db, user)
        if not user_org:
            return False
        return str(user_org.id) == str(required_org_id)
