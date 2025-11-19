"""
Authentication utilities for password hashing and JWT token management.

Security specifications:
- Bcrypt cost factor: 12 (as per CLAUDE.md requirements)
- JWT expiry: 30 minutes (configurable via settings)
- Algorithm: HS256
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Bcrypt password context with cost factor 12 (security requirement)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Cost factor for bcrypt
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with cost factor 12.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string

    Example:
        >>> hashed = hash_password("mySecurePassword123!")
        >>> isinstance(hashed, str)
        True
        >>> len(hashed) > 0
        True
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Previously hashed password

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("myPassword123!")
        >>> verify_password("myPassword123!", hashed)
        True
        >>> verify_password("wrongPassword", hashed)
        False
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Return False for any verification errors (malformed hash, etc.)
        return False


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing claims to encode in the token.
              Must include 'sub' (subject) claim.
        expires_delta: Optional custom expiration time.
                      Defaults to ACCESS_TOKEN_EXPIRE_MINUTES from settings.

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> isinstance(token, str)
        True
        >>> token.count(".")
        2
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    # Encode the JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string to decode

    Returns:
        Email (subject) from token if valid, None otherwise

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> email = decode_access_token(token)
        >>> email
        'user@example.com'
        >>> decode_access_token("invalid.token.string")
        None
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        # Extract email from 'sub' claim
        email: Optional[str] = payload.get("sub")

        if email is None:
            return None

        return email

    except JWTError:
        # Token is invalid, expired, or malformed
        return None
    except Exception:
        # Catch any other unexpected errors
        return None
