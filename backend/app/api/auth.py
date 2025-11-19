"""
Authentication API endpoints.

Endpoints:
    - POST /api/auth/register - Register a new user
    - POST /api/auth/login - Login and get JWT token
    - GET /api/auth/me - Get current user info
    - POST /api/auth/logout - Logout and invalidate token
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from app.services.redis_service import RedisService, get_redis
from app.utils.auth import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        UserResponse: Created user data (without password)

    Raises:
        HTTPException: If email is already registered (400)
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        native_language="en",
        target_proficiency="N3"
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
    redis: RedisService = Depends(get_redis)
) -> dict:
    """
    Login and get JWT access token.

    Args:
        login_data: User login credentials
        db: Database session
        redis: Redis service for session management

    Returns:
        Token: JWT access token and token type

    Raises:
        HTTPException: If credentials are invalid (401) or account is inactive (400)
    """
    # Get user from database
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user: User = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    await db.commit()

    # Create access token
    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user from dependency

    Returns:
        UserResponse: Current user data (without password)
    """
    return current_user


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis: RedisService = Depends(get_redis),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Logout and invalidate the current JWT token.

    Args:
        credentials: HTTP Bearer credentials containing JWT token
        redis: Redis service for token blacklisting
        current_user: Current authenticated user

    Returns:
        dict: Success message
    """
    token = credentials.credentials

    # Add token to blacklist in Redis
    # Token will be blacklisted for the remaining time until expiry
    await redis.blacklist_token(
        token=token,
        expire_seconds=settings.access_token_expire_minutes * 60
    )

    return {"message": "Successfully logged out"}
