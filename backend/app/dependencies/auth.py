"""
Authentication dependencies for protecting routes.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.redis_service import get_redis, RedisService
from app.utils.auth import decode_access_token

# HTTP Bearer authentication scheme
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    redis: RedisService = Depends(get_redis)
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials containing JWT token
        db: Database session
        redis: Redis service for checking token blacklist

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid, expired, or user not found

    Example:
        @app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.email}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Check if token is blacklisted (logged out)
    if await redis.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode token
    email = decode_access_token(token)

    if email is None:
        raise credentials_exception

    # Get user from database
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user: Optional[User] = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current authenticated and active user.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        User: Current active user

    Raises:
        HTTPException: If user account is inactive

    Example:
        @app.get("/active-only")
        async def active_route(user: User = Depends(get_current_active_user)):
            return {"user": user.email, "is_active": user.is_active}
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: AsyncSession = Depends(get_db),
    redis: RedisService = Depends(get_redis)
) -> Optional[User]:
    """
    Get the current authenticated user if credentials are provided.

    This dependency is optional and returns None if no credentials are provided
    or if the credentials are invalid.

    Args:
        credentials: Optional JWT Bearer credentials
        db: Database session
        redis: Redis service for checking token blacklist

    Returns:
        User object if authenticated, None otherwise

    Example:
        @app.get("/public-or-private")
        async def route(user: Optional[User] = Depends(get_optional_user)):
            if user:
                return {"message": f"Hello {user.email}"}
            return {"message": "Hello anonymous"}
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials

        # Check if token is blacklisted
        if await redis.is_token_blacklisted(token):
            return None

        # Decode token
        email = decode_access_token(token)

        if email is None:
            return None

        # Get user from database
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user: Optional[User] = result.scalar_one_or_none()

        if user is None or not user.is_active:
            return None

        return user

    except Exception:
        # If any error occurs, just return None (optional auth)
        return None
