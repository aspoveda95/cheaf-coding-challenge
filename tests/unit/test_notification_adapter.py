"""Tests for CeleryNotificationAdapter."""
# Standard Python Libraries
from unittest.mock import Mock, patch
from uuid import uuid4

# Third-Party Libraries
import pytest

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.user import User
from src.domain.value_objects.location import Location
from src.domain.value_objects.price import Price
from src.domain.value_objects.time_range import TimeRange
from src.domain.value_objects.user_segment import UserSegment
from src.infrastructure.adapters.notification_adapter import CeleryNotificationAdapter


class TestCeleryNotificationAdapter:
    """Test cases for CeleryNotificationAdapter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = CeleryNotificationAdapter()
        self.mock_celery = Mock()
        self.adapter._celery_app = self.mock_celery

        # Create test data
        self.user1 = User(
            id=uuid4(),
            email="user1@test.com",
            name="User 1",
            location=Location(40.7128, -74.0060),
            created_at="2023-01-01T00:00:00Z",
        )

        self.user2 = User(
            id=uuid4(),
            email="user2@test.com",
            name="User 2",
            location=Location(40.7589, -73.9851),
            created_at="2023-01-01T00:00:00Z",
        )

        self.promo = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(50.0),
            time_range=TimeRange("09:00:00", "18:00:00"),
            user_segments=[UserSegment.NEW_USERS, UserSegment.FREQUENT_BUYERS],
            max_radius_km=10.0,
        )

    def test_send_bulk_notifications_success(self):
        """Test successful bulk notification sending."""
        # Arrange
        users = [self.user1, self.user2]
        batch_size = 1000
        expected_task_id = "task-123"

        mock_task = Mock()
        mock_task.id = expected_task_id
        self.mock_celery.send_task.return_value = mock_task

        # Act
        result = self.adapter.send_bulk_notifications(users, self.promo, batch_size)

        # Assert
        assert result == expected_task_id
        self.mock_celery.send_task.assert_called_once()
        call_args = self.mock_celery.send_task.call_args
        assert call_args[1]["args"][1] == str(self.promo.id)
        assert call_args[1]["queue"] == "notifications"

    def test_send_bulk_notifications_default_batch_size(self):
        """Test bulk notifications with default batch size."""
        # Arrange
        users = [self.user1, self.user2]
        expected_task_id = "task-456"

        mock_task = Mock()
        mock_task.id = expected_task_id
        self.mock_celery.send_task.return_value = mock_task

        # Act
        result = self.adapter.send_bulk_notifications(users, self.promo)

        # Assert
        assert result == expected_task_id
        self.mock_celery.send_task.assert_called_once()

    def test_send_bulk_notifications_empty_users(self):
        """Test bulk notifications with empty user list."""
        # Arrange
        users = []
        expected_task_id = "task-789"

        mock_task = Mock()
        mock_task.id = expected_task_id
        self.mock_celery.send_task.return_value = mock_task

        # Act
        result = self.adapter.send_bulk_notifications(users, self.promo)

        # Assert
        assert result == expected_task_id
        self.mock_celery.send_task.assert_called_once()

    def test_send_immediate_notification_success(self):
        """Test successful immediate notification sending."""
        # Arrange
        message = "Custom message"
        expected_task_id = "task-immediate-123"

        mock_task = Mock()
        mock_task.id = expected_task_id
        self.mock_celery.send_task.return_value = mock_task

        # Act
        result = self.adapter.send_immediate_notification(
            self.user1, self.promo, message
        )

        # Assert
        assert result == expected_task_id
        self.mock_celery.send_task.assert_called_once()
        call_args = self.mock_celery.send_task.call_args
        assert call_args[1]["args"][0] == str(self.user1.id)
        assert call_args[1]["args"][1] == str(self.promo.id)
        assert call_args[1]["args"][2] == message
        assert call_args[1]["queue"] == "notifications_high_priority"

    def test_send_immediate_notification_no_message(self):
        """Test immediate notification without custom message."""
        # Arrange
        expected_task_id = "task-immediate-456"

        mock_task = Mock()
        mock_task.id = expected_task_id
        self.mock_celery.send_task.return_value = mock_task

        # Act
        result = self.adapter.send_immediate_notification(self.user1, self.promo)

        # Assert
        assert result == expected_task_id
        call_args = self.mock_celery.send_task.call_args
        assert call_args[1]["args"][2] is None

    def test_schedule_notification_success(self):
        """Test successful notification scheduling."""
        # Arrange
        users = [self.user1, self.user2]
        eta = "2023-12-31T23:59:59Z"
        expected_task_id = "task-scheduled-123"

        mock_task = Mock()
        mock_task.id = expected_task_id
        self.mock_celery.send_task.return_value = mock_task

        # Act
        result = self.adapter.schedule_notification(users, self.promo, eta)

        # Assert
        assert result == expected_task_id
        self.mock_celery.send_task.assert_called_once()
        call_args = self.mock_celery.send_task.call_args
        assert call_args[1]["args"][0] == [str(self.user1.id), str(self.user2.id)]
        assert call_args[1]["args"][1] == str(self.promo.id)
        assert call_args[1]["eta"] == eta
        assert call_args[1]["queue"] == "notifications_scheduled"

    def test_create_user_batches_single_batch(self):
        """Test user batching when all users fit in one batch."""
        # Arrange
        users = [self.user1, self.user2]
        batch_size = 10

        # Act
        result = self.adapter._create_user_batches(users, batch_size)

        # Assert
        assert len(result) == 1
        assert len(result[0]) == 2
        assert str(self.user1.id) in result[0]
        assert str(self.user2.id) in result[0]

    def test_create_user_batches_multiple_batches(self):
        """Test user batching when users need multiple batches."""
        # Arrange
        users = [self.user1, self.user2]
        batch_size = 1

        # Act
        result = self.adapter._create_user_batches(users, batch_size)

        # Assert
        assert len(result) == 2
        assert len(result[0]) == 1
        assert len(result[1]) == 1
        assert str(self.user1.id) in result[0]
        assert str(self.user2.id) in result[1]

    def test_create_user_batches_empty_list(self):
        """Test user batching with empty user list."""
        # Arrange
        users = []
        batch_size = 10

        # Act
        result = self.adapter._create_user_batches(users, batch_size)

        # Assert
        assert len(result) == 0

    def test_get_task_status_success(self):
        """Test successful task status retrieval."""
        # Arrange
        task_id = "task-123"
        mock_result = Mock()
        mock_result.status = "SUCCESS"
        mock_result.result = "Task completed"
        mock_result.ready.return_value = True
        self.mock_celery.AsyncResult.return_value = mock_result

        # Act
        result = self.adapter.get_task_status(task_id)

        # Assert
        assert result["task_id"] == task_id
        assert result["status"] == "SUCCESS"
        assert result["result"] == "Task completed"
        assert result["ready"] is True

    def test_get_task_status_pending(self):
        """Test task status retrieval for pending task."""
        # Arrange
        task_id = "task-456"
        mock_result = Mock()
        mock_result.status = "PENDING"
        mock_result.ready.return_value = False
        self.mock_celery.AsyncResult.return_value = mock_result

        # Act
        result = self.adapter.get_task_status(task_id)

        # Assert
        assert result["task_id"] == task_id
        assert result["status"] == "PENDING"
        assert result["result"] is None
        assert result["ready"] is False

    def test_get_task_status_failure(self):
        """Test task status retrieval for failed task."""
        # Arrange
        task_id = "task-789"
        mock_result = Mock()
        mock_result.status = "FAILURE"
        mock_result.result = "Task failed"
        mock_result.ready.return_value = True
        self.mock_celery.AsyncResult.return_value = mock_result

        # Act
        result = self.adapter.get_task_status(task_id)

        # Assert
        assert result["task_id"] == task_id
        assert result["status"] == "FAILURE"
        assert result["result"] == "Task failed"
        assert result["ready"] is True

    def test_get_task_status_exception(self):
        """Test task status retrieval when exception occurs."""
        # Arrange
        task_id = "task-error"
        self.mock_celery.AsyncResult.side_effect = Exception("Connection error")

        # Act
        result = self.adapter.get_task_status(task_id)

        # Assert
        assert result["task_id"] == task_id
        assert result["status"] == "ERROR"
        assert "Connection error" in result["error"]
        assert result["ready"] is True

    def test_get_task_status_celery_exception(self):
        """Test task status retrieval with Celery-specific exception."""
        # Arrange
        task_id = "task-celery-error"
        # Third-Party Libraries
        from celery.exceptions import Retry

        self.mock_celery.AsyncResult.side_effect = Retry("Retry error")

        # Act
        result = self.adapter.get_task_status(task_id)

        # Assert
        assert result["task_id"] == task_id
        assert result["status"] == "ERROR"
        assert "Retry error" in result["error"]
        assert result["ready"] is True
