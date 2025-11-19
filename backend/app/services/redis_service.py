"""
Redis service for session management and token blacklisting.
"""

import redis.asyncio as redis
from typing import Optional

from app.config import settings


class RedisService:
    """
    Service for Redis operations.

    Used for:
    - Token blacklisting (logout functionality)
    - Session management
    - Caching
    """

    def __init__(self):
        """Initialize Redis client."""
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    async def get(self, key: str) -> Optional[str]:
        """
        Get a value from Redis.

        Args:
            key: Redis key

        Returns:
            Value if exists, None otherwise
        """
        if not self.redis_client:
            await self.connect()
        return await self.redis_client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """
        Set a value in Redis.

        Args:
            key: Redis key
            value: Value to store
            expire: Optional expiration time in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            await self.connect()

        if expire:
            return await self.redis_client.setex(key, expire, value)
        else:
            return await self.redis_client.set(key, value)

    async def delete(self, key: str) -> int:
        """
        Delete a key from Redis.

        Args:
            key: Redis key to delete

        Returns:
            Number of keys deleted (0 or 1)
        """
        if not self.redis_client:
            await self.connect()
        return await self.redis_client.delete(key)

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.

        Args:
            key: Redis key to check

        Returns:
            True if key exists, False otherwise
        """
        if not self.redis_client:
            await self.connect()
        return await self.redis_client.exists(key) > 0

    # Token blacklist methods
    async def blacklist_token(
        self,
        token: str,
        expire_seconds: int = 1800  # 30 minutes default
    ) -> bool:
        """
        Add a token to the blacklist (for logout).

        Args:
            token: JWT token to blacklist
            expire_seconds: Time to keep token in blacklist (should match token expiry)

        Returns:
            True if successful
        """
        key = f"blacklist:{token}"
        return await self.set(key, "1", expire=expire_seconds)

    async def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            token: JWT token to check

        Returns:
            True if token is blacklisted, False otherwise
        """
        key = f"blacklist:{token}"
        return await self.exists(key)


# Global Redis service instance
redis_service = RedisService()


async def get_redis() -> RedisService:
    """
    Dependency for getting Redis service.

    Returns:
        RedisService: Global Redis service instance

    Example:
        @app.post("/logout")
        async def logout(
            token: str,
            redis: RedisService = Depends(get_redis)
        ):
            await redis.blacklist_token(token)
    """
    if not redis_service.redis_client:
        await redis_service.connect()
    return redis_service
