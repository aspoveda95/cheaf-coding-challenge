"""Tests for NotificationService."""
# Standard Python Libraries
from datetime import datetime
from unittest.mock import Mock, patch
from uuid import uuid4

# Third-Party Libraries
import pytest

# Local Libraries
from src.application.services.notification_service import (
    EmailNotificationChannel,
    NotificationChannel,
    NotificationService,
    PushNotificationChannel,
)
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.user import User
from src.domain.value_objects.location import Location
from src.domain.value_objects.price import Price
from src.domain.value_objects.time_range import TimeRange
from src.domain.value_objects.user_segment import UserSegment


class TestNotificationChannel:
    """Test cases for NotificationChannel abstract class."""

    def test_notification_channel_is_abstract(self):
        """Test that NotificationChannel is abstract."""
        # Act & Assert
        with pytest.raises(TypeError):
            NotificationChannel()


class TestEmailNotificationChannel:
    """Test cases for EmailNotificationChannel."""

    def setup_method(self):
        """Set up test fixtures."""
        self.channel = EmailNotificationChannel()
        self.user = User(
            id=uuid4(),
            email="test@example.com",
            name="Test User",
            location=Location(40.7128, -74.0060),
        )
        self.promo = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(50.0),
            time_range=TimeRange("09:00:00", "18:00:00"),
            user_segments=[UserSegment.NEW_USERS],
            max_radius_km=10.0,
        )

    def test_send_notification_success(self):
        """Test successful email notification."""
        # Arrange
        message = "Test message"

        # Act
        with patch("builtins.print") as mock_print:
            result = self.channel.send_notification(self.user, message, self.promo)

        # Assert
        assert result is True
        mock_print.assert_called_once_with(
            f"Email sent to {self.user.email}: {message}"
        )

    def test_send_notification_with_different_user(self):
        """Test email notification with different user."""
        # Arrange
        user2 = User(
            id=uuid4(),
            email="user2@example.com",
            name="User 2",
            location=Location(40.7589, -73.9851),
        )
        message = "Another message"

        # Act
        with patch("builtins.print") as mock_print:
            result = self.channel.send_notification(user2, message, self.promo)

        # Assert
        assert result is True
        mock_print.assert_called_once_with(f"Email sent to {user2.email}: {message}")


class TestPushNotificationChannel:
    """Test cases for PushNotificationChannel."""

    def setup_method(self):
        """Set up test fixtures."""
        self.channel = PushNotificationChannel()
        self.user = User(
            id=uuid4(),
            email="test@example.com",
            name="Test User",
            location=Location(40.7128, -74.0060),
        )
        self.promo = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(50.0),
            time_range=TimeRange("09:00:00", "18:00:00"),
            user_segments=[UserSegment.NEW_USERS],
            max_radius_km=10.0,
        )

    def test_send_notification_success(self):
        """Test successful push notification."""
        # Arrange
        message = "Test message"

        # Act
        with patch("builtins.print") as mock_print:
            result = self.channel.send_notification(self.user, message, self.promo)

        # Assert
        assert result is True
        mock_print.assert_called_once_with(
            f"Push notification sent to {self.user.id}: {message}"
        )

    def test_send_notification_with_different_user(self):
        """Test push notification with different user."""
        # Arrange
        user2 = User(
            id=uuid4(),
            email="user2@example.com",
            name="User 2",
            location=Location(40.7589, -73.9851),
        )
        message = "Another message"

        # Act
        with patch("builtins.print") as mock_print:
            result = self.channel.send_notification(user2, message, self.promo)

        # Assert
        assert result is True
        mock_print.assert_called_once_with(
            f"Push notification sent to {user2.id}: {message}"
        )


class TestNotificationService:
    """Test cases for NotificationService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.email_channel = Mock(spec=EmailNotificationChannel)
        self.push_channel = Mock(spec=PushNotificationChannel)
        self.channels = [self.email_channel, self.push_channel]
        self.service = NotificationService(self.channels)

        # Create test data
        self.user1 = User(
            id=uuid4(),
            email="user1@example.com",
            name="User 1",
            location=Location(40.7128, -74.0060),
        )
        self.user2 = User(
            id=uuid4(),
            email="user2@example.com",
            name="User 2",
            location=Location(40.7589, -73.9851),
        )
        self.promo = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(50.0),
            time_range=TimeRange("09:00:00", "18:00:00"),
            user_segments=[UserSegment.NEW_USERS],
            max_radius_km=10.0,
        )

    def test_send_flash_promo_notification_with_custom_message(self):
        """Test sending flash promo notification with custom message."""
        # Arrange
        users = [self.user1, self.user2]
        message = "Custom flash promo message"
        self.email_channel.send_notification.return_value = True
        self.push_channel.send_notification.return_value = True

        # Act
        result = self.service.send_flash_promo_notification(users, self.promo, message)

        # Assert
        assert result["total_users"] == 2
        assert result["successful_notifications"] == 2
        assert result["failed_notifications"] == 0
        assert result["duplicate_notifications"] == 0

        # Verify channels were called for each user
        assert self.email_channel.send_notification.call_count == 2
        assert self.push_channel.send_notification.call_count == 2

    def test_send_flash_promo_notification_without_message(self):
        """Test sending flash promo notification without custom message."""
        # Arrange
        users = [self.user1]
        self.email_channel.send_notification.return_value = True
        self.push_channel.send_notification.return_value = True

        # Act
        result = self.service.send_flash_promo_notification(users, self.promo)

        # Assert
        assert result["total_users"] == 1
        assert result["successful_notifications"] == 1
        assert result["failed_notifications"] == 0
        assert result["duplicate_notifications"] == 0

    def test_send_flash_promo_notification_with_failures(self):
        """Test sending flash promo notification with some failures."""
        # Arrange
        users = [self.user1, self.user2]
        message = "Test message"
        self.email_channel.send_notification.return_value = False
        self.push_channel.send_notification.return_value = False

        # Act
        result = self.service.send_flash_promo_notification(users, self.promo, message)

        # Assert
        assert result["total_users"] == 2
        assert result["successful_notifications"] == 0
        assert result["failed_notifications"] == 2
        assert result["duplicate_notifications"] == 0

    def test_send_flash_promo_notification_with_mixed_results(self):
        """Test sending flash promo notification with mixed success/failure."""
        # Arrange
        users = [self.user1, self.user2]
        message = "Test message"

        def mock_send_notification(user, message, promo):
            return user == self.user1  # Only user1 succeeds

        self.email_channel.send_notification.side_effect = mock_send_notification
        self.push_channel.send_notification.side_effect = mock_send_notification

        # Act
        result = self.service.send_flash_promo_notification(users, self.promo, message)

        # Assert
        assert result["total_users"] == 2
        assert result["successful_notifications"] == 1
        assert result["failed_notifications"] == 1
        assert result["duplicate_notifications"] == 0

    def test_send_flash_promo_notification_duplicate_prevention(self):
        """Test that duplicate notifications are prevented."""
        # Arrange
        users = [self.user1]
        message = "Test message"
        self.email_channel.send_notification.return_value = True
        self.push_channel.send_notification.return_value = True

        # Act - Send notification twice
        result1 = self.service.send_flash_promo_notification(users, self.promo, message)
        result2 = self.service.send_flash_promo_notification(users, self.promo, message)

        # Assert
        assert result1["successful_notifications"] == 1
        assert result1["duplicate_notifications"] == 0
        assert result2["successful_notifications"] == 0
        assert result2["duplicate_notifications"] == 1

    def test_send_flash_promo_notification_channel_exception(self):
        """Test handling of channel exceptions."""
        # Arrange
        users = [self.user1]
        message = "Test message"
        self.email_channel.send_notification.side_effect = Exception(
            "Email service down"
        )
        self.push_channel.send_notification.return_value = True

        # Act
        with patch("builtins.print") as mock_print:
            result = self.service.send_flash_promo_notification(
                users, self.promo, message
            )

        # Assert
        assert result["total_users"] == 1
        assert result["successful_notifications"] == 1  # Push notification succeeded
        assert result["failed_notifications"] == 0
        assert result["duplicate_notifications"] == 0
        mock_print.assert_called_once()

    def test_send_to_user_all_channels_fail(self):
        """Test _send_to_user when all channels fail."""
        # Arrange
        message = "Test message"
        self.email_channel.send_notification.return_value = False
        self.push_channel.send_notification.return_value = False

        # Act
        result = self.service._send_to_user(self.user1, message, self.promo)

        # Assert
        assert result is False

    def test_send_to_user_one_channel_succeeds(self):
        """Test _send_to_user when one channel succeeds."""
        # Arrange
        message = "Test message"
        self.email_channel.send_notification.return_value = False
        self.push_channel.send_notification.return_value = True

        # Act
        result = self.service._send_to_user(self.user1, message, self.promo)

        # Assert
        assert result is True

    def test_generate_promo_message_with_price_and_time(self):
        """Test _generate_promo_message with price and time range."""
        # Act
        message = self.service._generate_promo_message(self.promo)

        # Assert
        assert "FLASH PROMO ALERT" in message
        assert "Special price" in message
        assert "Valid" in message
        assert "Hurry up" in message

    def test_generate_promo_message_without_price_and_time(self):
        """Test _generate_promo_message without price and time range."""
        # Arrange
        promo_no_price_time = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=None,
            time_range=None,
            user_segments=[UserSegment.NEW_USERS],
            max_radius_km=10.0,
        )

        # Act
        message = self.service._generate_promo_message(promo_no_price_time)

        # Assert
        assert "FLASH PROMO ALERT" in message
        assert "Special Price" in message
        assert "Limited Time" in message
        assert "Hurry up" in message

    def test_send_bulk_notifications_success(self):
        """Test successful bulk notifications."""
        # Arrange
        user_batches = [[self.user1], [self.user2]]
        self.email_channel.send_notification.return_value = True
        self.push_channel.send_notification.return_value = True

        # Act
        result = self.service.send_bulk_notifications(user_batches, self.promo)

        # Assert
        assert result["total_batches"] == 2
        assert result["total_users"] == 2
        assert result["successful_notifications"] == 2
        assert result["failed_notifications"] == 0
        assert result["duplicate_notifications"] == 0

    def test_send_bulk_notifications_with_failures(self):
        """Test bulk notifications with some failures."""
        # Arrange
        user_batches = [[self.user1], [self.user2]]
        self.email_channel.send_notification.return_value = False
        self.push_channel.send_notification.return_value = False

        # Act
        result = self.service.send_bulk_notifications(user_batches, self.promo)

        # Assert
        assert result["total_batches"] == 2
        assert result["total_users"] == 2
        assert result["successful_notifications"] == 0
        assert result["failed_notifications"] == 2
        assert result["duplicate_notifications"] == 0

    def test_send_bulk_notifications_empty_batches(self):
        """Test bulk notifications with empty batches."""
        # Arrange
        user_batches = [[], []]

        # Act
        result = self.service.send_bulk_notifications(user_batches, self.promo)

        # Assert
        assert result["total_batches"] == 2
        assert result["total_users"] == 0
        assert result["successful_notifications"] == 0
        assert result["failed_notifications"] == 0
        assert result["duplicate_notifications"] == 0

    def test_clear_notification_history(self):
        """Test clearing notification history."""
        # Arrange
        users = [self.user1]
        message = "Test message"
        self.email_channel.send_notification.return_value = True
        self.push_channel.send_notification.return_value = True

        # Send notification to create history
        self.service.send_flash_promo_notification(users, self.promo, message)

        # Verify history exists
        assert len(self.service._sent_notifications) > 0

        # Act
        self.service.clear_notification_history()

        # Assert
        assert len(self.service._sent_notifications) == 0

    def test_send_flash_promo_notification_empty_users(self):
        """Test sending notification to empty user list."""
        # Arrange
        users = []
        message = "Test message"

        # Act
        result = self.service.send_flash_promo_notification(users, self.promo, message)

        # Assert
        assert result["total_users"] == 0
        assert result["successful_notifications"] == 0
        assert result["failed_notifications"] == 0
        assert result["duplicate_notifications"] == 0

    def test_send_bulk_notifications_mixed_results(self):
        """Test bulk notifications with mixed results."""
        # Arrange
        user_batches = [[self.user1], [self.user2]]

        def mock_send_notification(user, message, promo):
            return user == self.user1  # Only user1 succeeds

        self.email_channel.send_notification.side_effect = mock_send_notification
        self.push_channel.send_notification.side_effect = mock_send_notification

        # Act
        result = self.service.send_bulk_notifications(user_batches, self.promo)

        # Assert
        assert result["total_batches"] == 2
        assert result["total_users"] == 2
        assert result["successful_notifications"] == 1
        assert result["failed_notifications"] == 1
        assert result["duplicate_notifications"] == 0

    def test_send_flash_promo_notification_with_multiple_channels_success(self):
        """Test notification with multiple channels where some succeed."""
        # Arrange
        users = [self.user1]
        message = "Test message"
        self.email_channel.send_notification.return_value = True
        self.push_channel.send_notification.return_value = False

        # Act
        result = self.service.send_flash_promo_notification(users, self.promo, message)

        # Assert
        assert result["total_users"] == 1
        assert result["successful_notifications"] == 1  # At least one channel succeeded
        assert result["failed_notifications"] == 0
        assert result["duplicate_notifications"] == 0

    def test_send_flash_promo_notification_with_multiple_channels_all_fail(self):
        """Test notification with multiple channels where all fail."""
        # Arrange
        users = [self.user1]
        message = "Test message"
        self.email_channel.send_notification.return_value = False
        self.push_channel.send_notification.return_value = False

        # Act
        result = self.service.send_flash_promo_notification(users, self.promo, message)

        # Assert
        assert result["total_users"] == 1
        assert result["successful_notifications"] == 0
        assert result["failed_notifications"] == 1
        assert result["duplicate_notifications"] == 0
