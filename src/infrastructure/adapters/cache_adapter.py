"""Cache adapter for Redis operations."""
# Standard Python Libraries
import json
from typing import Any, Optional
from uuid import UUID

# Third-Party Libraries
from django.conf import settings
import redis


class CacheAdapter:
    """Redis cache adapter for Flash Promos."""

    def __init__(self):
        """Initialize CacheAdapter with Redis client."""
        self._redis_client = redis.from_url(settings.REDIS_URL)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self._redis_client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (redis.RedisError, json.JSONDecodeError):
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            serialized_value = json.dumps(value, default=str)
            return self._redis_client.setex(key, ttl, serialized_value)
        except (redis.RedisError, TypeError):
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self._redis_client.delete(key))
        except redis.RedisError:
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(self._redis_client.exists(key))
        except redis.RedisError:
            return False

    def set_with_lock(self, key: str, value: Any, ttl: int = 60) -> bool:
        """Set value with lock (for reservations)."""
        try:
            return self._redis_client.set(
                key, json.dumps(value, default=str), nx=True, ex=ttl
            )
        except (redis.RedisError, TypeError):
            return False

    def get_lock(self, key: str, ttl: int = 60) -> bool:
        """Get a lock."""
        try:
            return self._redis_client.set(key, "locked", nx=True, ex=ttl)
        except redis.RedisError:
            return False

    def release_lock(self, key: str) -> bool:
        """Release a lock."""
        try:
            return bool(self._redis_client.delete(key))
        except redis.RedisError:
            return False

    def get_active_promos_key(self) -> str:
        """Get cache key for active promos."""
        return "flash_promos:active"

    def get_user_segments_key(self, promo_id: UUID) -> str:
        """Get cache key for user segments of a promo."""
        return f"flash_promos:{promo_id}:segments"

    def get_reservation_key(self, product_id: UUID) -> str:
        """Get cache key for product reservation."""
        return f"reservation:{product_id}"

    def get_notification_key(self, user_id: UUID, promo_id: UUID, date: str) -> str:
        """Get cache key for notification tracking."""
        return f"notification:{user_id}:{promo_id}:{date}"

    def clear_promo_cache(self, promo_id: UUID) -> None:
        """Clear cache for a specific promo."""
        keys_to_delete = [
            self.get_user_segments_key(promo_id),
            f"flash_promos:{promo_id}:*",
        ]

        for key in keys_to_delete:
            if "*" in key:
                # Use pattern matching for wildcard keys
                for redis_key in self._redis_client.scan_iter(match=key):
                    self._redis_client.delete(redis_key)
            else:
                self._redis_client.delete(key)
