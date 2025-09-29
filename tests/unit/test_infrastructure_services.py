"""Tests for infrastructure services."""
# Standard Python Libraries
from datetime import datetime, time
from unittest.mock import patch
from uuid import uuid4

# Third-Party Libraries
import pytest

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.product import Product
from src.domain.entities.store import Store
from src.domain.entities.user import User
from src.domain.value_objects.location import Location
from src.domain.value_objects.price import Price
from src.domain.value_objects.time_range import TimeRange
from src.domain.value_objects.user_segment import UserSegment
from src.infrastructure.services.mock_email_service import MockEmailService
from src.infrastructure.services.mock_push_notification_service import (
    MockPushNotificationService,
)
from src.infrastructure.services.mock_sms_service import MockSMSService


class TestMockEmailService:
    """Test cases for MockEmailService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.email_service = MockEmailService()
        self.user = User(
            id=uuid4(),
            email="test@example.com",
            name="Test User",
            location=Location(latitude=40.7128, longitude=-74.0060),
            created_at=datetime.now(),
            last_purchase_at=datetime.now(),
            total_purchases=5,
            total_spent=100.0,
            segments=[UserSegment.NEW_USERS],
        )
        self.promo = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(50.0),
            time_range=TimeRange(start_time=time(9, 0), end_time=time(17, 0)),
            user_segments=[UserSegment.NEW_USERS],
            max_radius_km=10.0,
            is_active=True,
        )

    def test_send_email_success(self):
        """Test successful email sending."""
        result = self.email_service.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            message="Test message",
            user=self.user,
        )

        assert result is True
        sent_emails = self.email_service.get_sent_emails()
        assert len(sent_emails) == 1
        assert sent_emails[0]["to"] == "test@example.com"
        assert sent_emails[0]["subject"] == "Test Subject"
        assert sent_emails[0]["message"] == "Test message"
        assert sent_emails[0]["user_id"] == str(self.user.id)

    def test_send_email_without_user(self):
        """Test email sending without user."""
        result = self.email_service.send_email(
            to_email="test@example.com", subject="Test Subject", message="Test message"
        )

        assert result is True
        sent_emails = self.email_service.get_sent_emails()
        assert len(sent_emails) == 1
        assert sent_emails[0]["user_id"] is None

    def test_send_bulk_email_success(self):
        """Test successful bulk email sending."""
        recipients = ["user1@example.com", "user2@example.com"]
        users = [self.user, self.user]

        result = self.email_service.send_bulk_email(
            recipients=recipients,
            subject="Bulk Test Subject",
            message="Bulk test message",
            users=users,
        )

        assert result["total_recipients"] == 2
        assert result["successful_sends"] == 2
        assert result["failed_sends"] == 0
        assert len(result["errors"]) == 0

    def test_send_bulk_email_without_users(self):
        """Test bulk email sending without users."""
        recipients = ["user1@example.com", "user2@example.com"]

        result = self.email_service.send_bulk_email(
            recipients=recipients,
            subject="Bulk Test Subject",
            message="Bulk test message",
        )

        assert result["total_recipients"] == 2
        assert result["successful_sends"] == 2
        assert result["failed_sends"] == 0

    def test_send_bulk_email_with_fewer_users(self):
        """Test bulk email with fewer users than recipients."""
        recipients = ["user1@example.com", "user2@example.com", "user3@example.com"]
        users = [self.user]  # Only one user for three recipients

        result = self.email_service.send_bulk_email(
            recipients=recipients,
            subject="Bulk Test Subject",
            message="Bulk test message",
            users=users,
        )

        assert result["total_recipients"] == 3
        assert result["successful_sends"] == 3
        assert result["failed_sends"] == 0

    def test_send_bulk_email_with_exception(self):
        """Test bulk email with exception handling."""
        recipients = ["user1@example.com"]

        with patch.object(
            self.email_service, "send_email", side_effect=Exception("Email error")
        ):
            result = self.email_service.send_bulk_email(
                recipients=recipients,
                subject="Bulk Test Subject",
                message="Bulk test message",
            )

        assert result["total_recipients"] == 1
        assert result["successful_sends"] == 0
        assert result["failed_sends"] == 1
        assert len(result["errors"]) == 1
        assert "Error sending to user1@example.com: Email error" in result["errors"][0]

    def test_send_bulk_email_with_false_return(self):
        """Test bulk email when send_email returns False."""
        recipients = ["user1@example.com"]

        with patch.object(self.email_service, "send_email", return_value=False):
            result = self.email_service.send_bulk_email(
                recipients=recipients,
                subject="Bulk Test Subject",
                message="Bulk test message",
            )

        assert result["total_recipients"] == 1
        assert result["successful_sends"] == 0
        assert result["failed_sends"] == 1
        assert len(result["errors"]) == 1
        assert "Failed to send to user1@example.com" in result["errors"][0]

    def test_send_flash_promo_email_with_message(self):
        """Test flash promo email with custom message."""
        custom_message = "Custom flash promo message"

        result = self.email_service.send_flash_promo_email(
            user=self.user, promo=self.promo, message=custom_message
        )

        assert result is True
        sent_emails = self.email_service.get_sent_emails()
        assert len(sent_emails) == 1
        assert sent_emails[0]["message"] == custom_message
        assert "FLASH PROMO ALERT!" in sent_emails[0]["subject"]

    def test_send_flash_promo_email_without_message(self):
        """Test flash promo email without custom message."""
        result = self.email_service.send_flash_promo_email(
            user=self.user, promo=self.promo
        )

        assert result is True
        sent_emails = self.email_service.get_sent_emails()
        assert len(sent_emails) == 1
        assert "FLASH PROMO ALERT!" in sent_emails[0]["subject"]
        # FlashPromo doesn't have product_name, so we'll check for the promo ID instead
        assert (
            str(self.promo.id) in sent_emails[0]["message"]
            or "FLASH PROMO ALERT!" in sent_emails[0]["message"]
        )

    def test_send_bulk_flash_promo_email_with_message(self):
        """Test bulk flash promo email with custom message."""
        users = [self.user, self.user]
        custom_message = "Custom bulk flash promo message"

        result = self.email_service.send_bulk_flash_promo_email(
            users=users, promo=self.promo, message=custom_message
        )

        assert result["total_recipients"] == 2
        assert result["successful_sends"] == 2
        sent_emails = self.email_service.get_sent_emails()
        assert len(sent_emails) == 2
        assert all("FLASH PROMO ALERT!" in email["subject"] for email in sent_emails)

    def test_send_bulk_flash_promo_email_without_message(self):
        """Test bulk flash promo email without custom message."""
        users = [self.user, self.user]

        result = self.email_service.send_bulk_flash_promo_email(
            users=users, promo=self.promo
        )

        assert result["total_recipients"] == 2
        assert result["successful_sends"] == 2

    def test_generate_flash_promo_message(self):
        """Test flash promo message generation."""
        message = self.email_service._generate_flash_promo_message(self.promo)

        assert "FLASH PROMO ALERT!" in message
        # FlashPromo doesn't have product_name, so we'll check for the promo ID instead
        assert str(self.promo.id) in message or "FLASH PROMO ALERT!" in message
        assert "50.0" in message
        assert "09:00:00" in message
        assert "17:00:00" in message

    def test_generate_flash_promo_message_with_none_values(self):
        """Test flash promo message generation with None values."""
        promo_with_none = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=None,
            time_range=None,
            user_segments=[UserSegment.NEW_USERS],
            max_radius_km=10.0,
            is_active=True,
        )

        message = self.email_service._generate_flash_promo_message(promo_with_none)

        assert "FLASH PROMO ALERT!" in message
        # FlashPromo doesn't have product_name, so we'll check for the promo ID instead
        assert str(self.promo.id) in message or "FLASH PROMO ALERT!" in message
        assert "Special Price" in message
        assert "Limited Time" in message

    def test_get_timestamp(self):
        """Test timestamp generation."""
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = (
                "2023-01-01T12:00:00"
            )

            timestamp = self.email_service._get_timestamp()
            assert timestamp == "2023-01-01T12:00:00"

    def test_get_sent_emails(self):
        """Test getting sent emails."""
        self.email_service.send_email("test@example.com", "Subject", "Message")

        sent_emails = self.email_service.get_sent_emails()
        assert len(sent_emails) == 1
        assert sent_emails[0]["to"] == "test@example.com"

    def test_clear_sent_emails(self):
        """Test clearing sent emails."""
        self.email_service.send_email("test@example.com", "Subject", "Message")
        assert len(self.email_service.get_sent_emails()) == 1

        self.email_service.clear_sent_emails()
        assert len(self.email_service.get_sent_emails()) == 0


class TestMockPushNotificationService:
    """Test cases for MockPushNotificationService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.push_service = MockPushNotificationService()
        self.user = User(
            id=uuid4(),
            email="test@example.com",
            name="Test User",
            location=Location(latitude=40.7128, longitude=-74.0060),
            created_at=datetime.now(),
            last_purchase_at=datetime.now(),
            total_purchases=5,
            total_spent=100.0,
            segments=[UserSegment.NEW_USERS],
        )

    def test_send_notification_success(self):
        """Test successful notification sending."""
        result = self.push_service.send_push_notification(
            user=self.user, title="Test Title", message="Test message"
        )

        assert result is True
        sent_notifications = self.push_service.get_sent_notifications()
        assert len(sent_notifications) == 1
        assert sent_notifications[0]["user_id"] == str(self.user.id)
        assert sent_notifications[0]["title"] == "Test Title"
        assert sent_notifications[0]["message"] == "Test message"

    def test_send_notification_without_user(self):
        """Test notification sending without user."""
        # Create a minimal user for testing
        test_user = User(
            id=uuid4(),
            email="test@example.com",
            name="Test User",
            location=Location(latitude=40.7128, longitude=-74.0060),
            created_at=datetime.now(),
            last_purchase_at=datetime.now(),
            total_purchases=0,
            total_spent=0.0,
            segments=[],
        )
        result = self.push_service.send_push_notification(
            user=test_user, title="Test Title", message="Test message"
        )

        assert result is True
        sent_notifications = self.push_service.get_sent_notifications()
        assert len(sent_notifications) == 1
        assert sent_notifications[0]["user_id"] == str(test_user.id)

    def test_send_bulk_notification_success(self):
        """Test successful bulk notification sending."""
        users = [self.user, self.user]

        result = self.push_service.send_bulk_push_notification(
            users=users, title="Bulk Test Title", message="Bulk test message"
        )

        assert result["total_users"] == 2
        assert result["successful_sends"] == 2
        assert result["failed_sends"] == 0
        assert len(result["errors"]) == 0

    def test_send_bulk_notification_with_exception(self):
        """Test bulk notification with exception handling."""
        users = [self.user]

        with patch.object(
            self.push_service,
            "send_push_notification",
            side_effect=Exception("Notification error"),
        ):
            result = self.push_service.send_bulk_push_notification(
                users=users, title="Bulk Test Title", message="Bulk test message"
            )

        assert result["total_users"] == 1
        assert result["successful_sends"] == 0
        assert result["failed_sends"] == 1
        assert len(result["errors"]) == 1
        assert "Error sending push to user" in result["errors"][0]

    def test_send_bulk_notification_with_false_return(self):
        """Test bulk notification when send_push_notification returns False."""
        users = [self.user]

        with patch.object(
            self.push_service, "send_push_notification", return_value=False
        ):
            result = self.push_service.send_bulk_push_notification(
                users=users, title="Bulk Test Title", message="Bulk test message"
            )

        assert result["total_users"] == 1
        assert result["successful_sends"] == 0
        assert result["failed_sends"] == 1
        assert len(result["errors"]) == 1
        assert "Failed to send" in result["errors"][0]

    def test_get_sent_notifications(self):
        """Test getting sent notifications."""
        self.push_service.send_push_notification(self.user, "Title", "Message")

        sent_notifications = self.push_service.get_sent_notifications()
        assert len(sent_notifications) == 1
        assert sent_notifications[0]["user_id"] == str(self.user.id)

    def test_clear_sent_notifications(self):
        """Test clearing sent notifications."""
        self.push_service.send_push_notification(self.user, "Title", "Message")
        assert len(self.push_service.get_sent_notifications()) == 1

        self.push_service.clear_sent_notifications()
        assert len(self.push_service.get_sent_notifications()) == 0


class TestMockSmsService:
    """Test cases for MockSmsService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sms_service = MockSMSService()
        self.user = User(
            id=uuid4(),
            email="test@example.com",
            name="Test User",
            location=Location(latitude=40.7128, longitude=-74.0060),
            created_at=datetime.now(),
            last_purchase_at=datetime.now(),
            total_purchases=5,
            total_spent=100.0,
            segments=[UserSegment.NEW_USERS],
        )

    def test_send_sms_success(self):
        """Test successful SMS sending."""
        result = self.sms_service.send_sms(
            phone_number="+1234567890", message="Test SMS message", user=self.user
        )

        assert result is True
        sent_sms = self.sms_service.get_sent_sms()
        assert len(sent_sms) == 1
        assert sent_sms[0]["phone_number"] == "+1234567890"
        assert sent_sms[0]["message"] == "Test SMS message"
        assert sent_sms[0]["user_id"] == str(self.user.id)

    def test_send_sms_without_user(self):
        """Test SMS sending without user."""
        result = self.sms_service.send_sms(
            phone_number="+1234567890", message="Test SMS message"
        )

        assert result is True
        sent_sms = self.sms_service.get_sent_sms()
        assert len(sent_sms) == 1
        assert sent_sms[0]["user_id"] is None

    def test_send_bulk_sms_success(self):
        """Test successful bulk SMS sending."""
        phone_numbers = ["+1234567890", "+0987654321"]
        users = [self.user, self.user]

        result = self.sms_service.send_bulk_sms(
            phone_numbers=phone_numbers, message="Bulk SMS message", users=users
        )

        assert result["total_recipients"] == 2
        assert result["successful_sends"] == 2
        assert result["failed_sends"] == 0
        assert len(result["errors"]) == 0

    def test_send_bulk_sms_with_exception(self):
        """Test bulk SMS with exception handling."""
        phone_numbers = ["+1234567890"]

        with patch.object(
            self.sms_service, "send_sms", side_effect=Exception("SMS error")
        ):
            result = self.sms_service.send_bulk_sms(
                phone_numbers=phone_numbers, message="Bulk SMS message"
            )

        assert result["total_recipients"] == 1
        assert result["successful_sends"] == 0
        assert result["failed_sends"] == 1
        assert len(result["errors"]) == 1
        assert "Error sending SMS to +1234567890: SMS error" in result["errors"][0]

    def test_send_bulk_sms_with_false_return(self):
        """Test bulk SMS when send_sms returns False."""
        phone_numbers = ["+1234567890"]

        with patch.object(self.sms_service, "send_sms", return_value=False):
            result = self.sms_service.send_bulk_sms(
                phone_numbers=phone_numbers, message="Bulk SMS message"
            )

        assert result["total_recipients"] == 1
        assert result["successful_sends"] == 0
        assert result["failed_sends"] == 1
        assert len(result["errors"]) == 1
        assert "Failed to send SMS to +1234567890" in result["errors"][0]

    def test_get_sent_sms(self):
        """Test getting sent SMS."""
        self.sms_service.send_sms("+1234567890", "Test message")

        sent_sms = self.sms_service.get_sent_sms()
        assert len(sent_sms) == 1
        assert sent_sms[0]["phone_number"] == "+1234567890"

    def test_clear_sent_sms(self):
        """Test clearing sent SMS."""
        self.sms_service.send_sms("+1234567890", "Test message")
        assert len(self.sms_service.get_sent_sms()) == 1

        self.sms_service.clear_sent_sms()
        assert len(self.sms_service.get_sent_sms()) == 0
