"""Tests for CacheAdapter."""
# Standard Python Libraries
from unittest.mock import Mock, patch
from uuid import uuid4

# Third-Party Libraries
import pytest
import redis

# Local Libraries
from src.infrastructure.adapters.cache_adapter import CacheAdapter


class TestCacheAdapter:
    """Test cases for CacheAdapter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cache_adapter = CacheAdapter()
        self.mock_redis = Mock()
        self.cache_adapter._redis_client = self.mock_redis

    def test_get_success(self):
        """Test successful cache get operation."""
        # Arrange
        key = "test_key"
        expected_value = {"data": "test"}
        self.mock_redis.get.return_value = '{"data": "test"}'

        # Act
        result = self.cache_adapter.get(key)

        # Assert
        assert result == expected_value
        self.mock_redis.get.assert_called_once_with(key)

    def test_get_none_value(self):
        """Test cache get when value is None."""
        # Arrange
        key = "test_key"
        self.mock_redis.get.return_value = None

        # Act
        result = self.cache_adapter.get(key)

        # Assert
        assert result is None
        self.mock_redis.get.assert_called_once_with(key)

    def test_get_redis_error(self):
        """Test cache get with Redis error."""
        # Arrange
        key = "test_key"
        self.mock_redis.get.side_effect = redis.RedisError("Connection error")

        # Act
        result = self.cache_adapter.get(key)

        # Assert
        assert result is None

    def test_get_json_decode_error(self):
        """Test cache get with JSON decode error."""
        # Arrange
        key = "test_key"
        self.mock_redis.get.return_value = "invalid_json"

        # Act
        result = self.cache_adapter.get(key)

        # Assert
        assert result is None

    def test_set_success(self):
        """Test successful cache set operation."""
        # Arrange
        key = "test_key"
        value = {"data": "test"}
        ttl = 3600
        self.mock_redis.setex.return_value = True

        # Act
        result = self.cache_adapter.set(key, value, ttl)

        # Assert
        assert result is True
        self.mock_redis.setex.assert_called_once()

    def test_set_redis_error(self):
        """Test cache set with Redis error."""
        # Arrange
        key = "test_key"
        value = {"data": "test"}
        self.mock_redis.setex.side_effect = redis.RedisError("Connection error")

        # Act
        result = self.cache_adapter.set(key, value)

        # Assert
        assert result is False

    def test_set_type_error(self):
        """Test cache set with TypeError."""
        # Arrange
        key = "test_key"
        value = object()  # Non-serializable object
        self.mock_redis.setex.side_effect = TypeError("Not serializable")

        # Act
        result = self.cache_adapter.set(key, value)

        # Assert
        assert result is False

    def test_delete_success(self):
        """Test successful cache delete operation."""
        # Arrange
        key = "test_key"
        self.mock_redis.delete.return_value = 1

        # Act
        result = self.cache_adapter.delete(key)

        # Assert
        assert result is True
        self.mock_redis.delete.assert_called_once_with(key)

    def test_delete_not_found(self):
        """Test cache delete when key doesn't exist."""
        # Arrange
        key = "test_key"
        self.mock_redis.delete.return_value = 0

        # Act
        result = self.cache_adapter.delete(key)

        # Assert
        assert result is False

    def test_delete_redis_error(self):
        """Test cache delete with Redis error."""
        # Arrange
        key = "test_key"
        self.mock_redis.delete.side_effect = redis.RedisError("Connection error")

        # Act
        result = self.cache_adapter.delete(key)

        # Assert
        assert result is False

    def test_exists_true(self):
        """Test cache exists when key exists."""
        # Arrange
        key = "test_key"
        self.mock_redis.exists.return_value = 1

        # Act
        result = self.cache_adapter.exists(key)

        # Assert
        assert result is True
        self.mock_redis.exists.assert_called_once_with(key)

    def test_exists_false(self):
        """Test cache exists when key doesn't exist."""
        # Arrange
        key = "test_key"
        self.mock_redis.exists.return_value = 0

        # Act
        result = self.cache_adapter.exists(key)

        # Assert
        assert result is False

    def test_exists_redis_error(self):
        """Test cache exists with Redis error."""
        # Arrange
        key = "test_key"
        self.mock_redis.exists.side_effect = redis.RedisError("Connection error")

        # Act
        result = self.cache_adapter.exists(key)

        # Assert
        assert result is False

    def test_set_with_lock_success(self):
        """Test successful set with lock operation."""
        # Arrange
        key = "test_key"
        value = {"data": "test"}
        ttl = 60
        self.mock_redis.set.return_value = True

        # Act
        result = self.cache_adapter.set_with_lock(key, value, ttl)

        # Assert
        assert result is True
        self.mock_redis.set.assert_called_once()

    def test_set_with_lock_redis_error(self):
        """Test set with lock with Redis error."""
        # Arrange
        key = "test_key"
        value = {"data": "test"}
        self.mock_redis.set.side_effect = redis.RedisError("Connection error")

        # Act
        result = self.cache_adapter.set_with_lock(key, value)

        # Assert
        assert result is False

    def test_set_with_lock_type_error(self):
        """Test set with lock with TypeError."""
        # Arrange
        key = "test_key"
        value = object()  # Non-serializable object
        self.mock_redis.set.side_effect = TypeError("Not serializable")

        # Act
        result = self.cache_adapter.set_with_lock(key, value)

        # Assert
        assert result is False

    def test_get_lock_success(self):
        """Test successful get lock operation."""
        # Arrange
        key = "test_key"
        ttl = 60
        self.mock_redis.set.return_value = True

        # Act
        result = self.cache_adapter.get_lock(key, ttl)

        # Assert
        assert result is True
        self.mock_redis.set.assert_called_once()

    def test_get_lock_redis_error(self):
        """Test get lock with Redis error."""
        # Arrange
        key = "test_key"
        self.mock_redis.set.side_effect = redis.RedisError("Connection error")

        # Act
        result = self.cache_adapter.get_lock(key)

        # Assert
        assert result is False

    def test_release_lock_success(self):
        """Test successful release lock operation."""
        # Arrange
        key = "test_key"
        self.mock_redis.delete.return_value = 1

        # Act
        result = self.cache_adapter.release_lock(key)

        # Assert
        assert result is True
        self.mock_redis.delete.assert_called_once_with(key)

    def test_release_lock_redis_error(self):
        """Test release lock with Redis error."""
        # Arrange
        key = "test_key"
        self.mock_redis.delete.side_effect = redis.RedisError("Connection error")

        # Act
        result = self.cache_adapter.release_lock(key)

        # Assert
        assert result is False

    def test_get_active_promos_key(self):
        """Test get active promos cache key."""
        # Act
        result = self.cache_adapter.get_active_promos_key()

        # Assert
        assert result == "flash_promos:active"

    def test_get_user_segments_key(self):
        """Test get user segments cache key."""
        # Arrange
        promo_id = uuid4()

        # Act
        result = self.cache_adapter.get_user_segments_key(promo_id)

        # Assert
        assert result == f"flash_promos:{promo_id}:segments"

    def test_get_reservation_key(self):
        """Test get reservation cache key."""
        # Arrange
        product_id = uuid4()

        # Act
        result = self.cache_adapter.get_reservation_key(product_id)

        # Assert
        assert result == f"reservation:{product_id}"

    def test_get_notification_key(self):
        """Test get notification cache key."""
        # Arrange
        user_id = uuid4()
        promo_id = uuid4()
        date = "2023-01-01"

        # Act
        result = self.cache_adapter.get_notification_key(user_id, promo_id, date)

        # Assert
        assert result == f"notification:{user_id}:{promo_id}:{date}"

    def test_clear_promo_cache_simple_key(self):
        """Test clear promo cache for simple keys."""
        # Arrange
        promo_id = uuid4()
        self.mock_redis.delete.return_value = 1
        self.mock_redis.scan_iter.return_value = iter([])  # No wildcard matches

        # Act
        self.cache_adapter.clear_promo_cache(promo_id)

        # Assert
        expected_key = f"flash_promos:{promo_id}:segments"
        self.mock_redis.delete.assert_called_with(expected_key)

    def test_clear_promo_cache_wildcard_key(self):
        """Test clear promo cache for wildcard keys."""
        # Arrange
        promo_id = uuid4()
        wildcard_key = f"flash_promos:{promo_id}:*"
        matching_keys = [
            f"flash_promos:{promo_id}:key1",
            f"flash_promos:{promo_id}:key2",
        ]

        self.mock_redis.scan_iter.return_value = iter(matching_keys)
        self.mock_redis.delete.return_value = 1

        # Act
        self.cache_adapter.clear_promo_cache(promo_id)

        # Assert
        # Should call scan_iter for wildcard pattern
        self.mock_redis.scan_iter.assert_called_with(match=wildcard_key)
        # Should delete each matching key
        assert (
            self.mock_redis.delete.call_count == len(matching_keys) + 1
        )  # +1 for simple key

    def test_clear_promo_cache_no_matching_keys(self):
        """Test clear promo cache when no keys match wildcard."""
        # Arrange
        promo_id = uuid4()
        self.mock_redis.scan_iter.return_value = iter([])
        self.mock_redis.delete.return_value = 1

        # Act
        self.cache_adapter.clear_promo_cache(promo_id)

        # Assert
        # Should only delete the simple key, not iterate through wildcard
        assert self.mock_redis.delete.call_count == 1
