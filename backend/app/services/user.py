from sqlalchemy.orm import Session
from typing import Optional
from ..models.user import User
from ..models.organization import Organization, OrganizationMembership
from ..schemas.user import UserCreate, UserUpdate
from ..schemas.auth import UserRegister
from .auth import AuthService
from datetime import datetime
import uuid


class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserRegister) -> User:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("User with this email already exists")

        # Create user
        hashed_password = AuthService.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            encrypted_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone
        )
        db.add(db_user)
        db.flush()  # Get the user ID

        # Create organization if provided
        if user_data.organization_name:
            org = Organization(
                name=user_data.organization_name,
                type='law_firm'
            )
            db.add(org)
            db.flush()  # Get the org ID

            # Create membership
            membership = OrganizationMembership(
                org_id=org.id,
                user_id=db_user.id,
                role='owner',
                status='active',
                joined_at=datetime.utcnow()
            )
            db.add(membership)

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        return db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()

    @staticmethod
    def update_user(db: Session, user_id: uuid.UUID, user_data: UserUpdate) -> Optional[User]:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_last_login(db: Session, user_id: uuid.UUID):
        user = UserService.get_user_by_id(db, user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            db.commit()