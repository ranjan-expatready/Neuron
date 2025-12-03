from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.user import User as UserModel
from ...schemas.user import User, UserUpdate
from ...services.user import UserService
from ..dependencies import get_current_user

router = APIRouter()


@router.get("/me", response_model=User)
async def get_current_user_profile(current_user: UserModel = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=User)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user profile"""
    updated_user = UserService.update_user(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user
