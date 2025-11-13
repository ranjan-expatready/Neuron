from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv

from ..models.user import User
from ..models.organization import Organization, OrganizationMembership
from ..schemas.auth import TokenData

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

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
        user = db.query(User).filter(User.email == token_data.email, User.deleted_at.is_(None)).first()
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    def get_user_organization(db: Session, user: User) -> Optional[Organization]:
        membership = db.query(OrganizationMembership).filter(
            OrganizationMembership.user_id == user.id,
            OrganizationMembership.status == 'active'
        ).first()
        
        if not membership:
            return None
            
        return db.query(Organization).filter(
            Organization.id == membership.org_id,
            Organization.deleted_at.is_(None)
        ).first()

    @staticmethod
    def check_org_permission(db: Session, user: User, required_org_id: str) -> bool:
        """Check if user has access to the specified organization"""
        user_org = AuthService.get_user_organization(db, user)
        if not user_org:
            return False
        return str(user_org.id) == str(required_org_id)