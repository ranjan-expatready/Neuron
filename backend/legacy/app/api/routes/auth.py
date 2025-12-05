from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...schemas.auth import Token, UserLogin, UserRegister
from ...schemas.user import User
from ...services.auth import AuthService
from ...services.user import UserService

router = APIRouter()


@router.post("/register", response_model=User)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    import logging
    import traceback

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Attempting to register user: {user_data.email}")
        logger.info(
            "Password length: %s chars, %s bytes",
            len(user_data.password),
            len(user_data.password.encode("utf-8")),
        )

        # Create user - password hashing is handled in UserService.create_user
        # which has proper error handling for password hashing issues
        user = UserService.create_user(db, user_data)
        logger.info(f"User registered successfully: {user.email}")
        return user
    except ValueError as ve:
        error_msg = str(ve)
        logger.error(f"ValueError in UserService.create_user: {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Re-raise to be caught by outer handler
        raise
    except ValueError as e:
        error_msg = str(e)
        logger.error(f"ValueError during registration: {error_msg}")
        # Check if it's a user already exists error
        if "already exists" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
        # Check if it's the password length error (shouldn't happen with our fix, but handle it)
        if "72 bytes" in error_msg or "longer than" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password processing error. Please try a different password.",
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Exception during registration: {error_msg}", exc_info=True)
        # Check if it's the password length error
        if "72 bytes" in error_msg or "longer than" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password processing error. Please try a different password.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user"
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with email and password"""
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=AuthService.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Update last login
    UserService.update_last_login(db, user.id)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login-json", response_model=Token)
async def login_json(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login with JSON payload"""
    user = AuthService.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=AuthService.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Update last login
    UserService.update_last_login(db, user.id)

    return {"access_token": access_token, "token_type": "bearer"}
