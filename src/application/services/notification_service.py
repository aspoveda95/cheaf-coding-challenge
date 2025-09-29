"""Notification service for Flash Promos."""
# Standard Python Libraries
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.user import User


class NotificationChannel(ABC):
    """Abstract base class for notification channels."""

    @abstractmethod
    def send_notification(self, user: User, message: str, promo: FlashPromo) -> bool:
        """Send notification to user."""
        pass


class EmailNotificationChannel(NotificationChannel):
    """Email notification channel implementation."""

    def send_notification(self, user: User, message: str, promo: FlashPromo) -> bool:
        """Send email notification."""
        # Implementation would integrate with email service
        print(f"Email sent to {user.email}: {message}")
        return True


class PushNotificationChannel(NotificationChannel):
    """Push notification channel implementation."""

    def send_notification(self, user: User, message: str, promo: FlashPromo) -> bool:
        """Send push notification."""
        # Implementation would integrate with push notification service
        print(f"Push notification sent to {user.id}: {message}")
        return True


class NotificationService:
    """Service for managing notifications across multiple channels."""

    def __init__(self, channels: List[NotificationChannel]):
        """Initialize NotificationService with notification channels."""
        self._channels = channels
        self._sent_notifications = set()

    def send_flash_promo_notification(
        self, users: List[User], promo: FlashPromo, message: Optional[str] = None
    ) -> dict:
        """Send flash promo notifications to users.

        Args:
            users: List of users to notify
            promo: Flash promo to notify about
            message: Custom message (optional)

        Returns:
            Dictionary with notification results
        """
        if not message:
            message = self._generate_promo_message(promo)

        results = {
            "total_users": len(users),
            "successful_notifications": 0,
            "failed_notifications": 0,
            "duplicate_notifications": 0,
        }

        for user in users:
            notification_key = f"{user.id}:{promo.id}:{datetime.now().date()}"

            if notification_key in self._sent_notifications:
                results["duplicate_notifications"] += 1
                continue

            success = self._send_to_user(user, message, promo)

            if success:
                results["successful_notifications"] += 1
                self._sent_notifications.add(notification_key)
            else:
                results["failed_notifications"] += 1

        return results

    def _send_to_user(self, user: User, message: str, promo: FlashPromo) -> bool:
        """Send notification to a single user through all channels."""
        success = False

        for channel in self._channels:
            try:
                if channel.send_notification(user, message, promo):
                    success = True
            except Exception as e:
                print(
                    f"Failed to send notification via {channel.__class__.__name__}: {e}"
                )

        return success

    def _generate_promo_message(self, promo: FlashPromo) -> str:
        """Generate a flash promo notification message."""
        price_str = str(promo.promo_price) if promo.promo_price else "Special Price"
        time_str = str(promo.time_range) if promo.time_range else "Limited Time"

        return (
            f"🔥 FLASH PROMO ALERT! 🔥\n"
            f"Special price: {price_str}\n"
            f"Valid: {time_str}\n"
            f"Hurry up! Limited time offer!"
        )

    def send_bulk_notifications(
        self, user_batches: List[List[User]], promo: FlashPromo
    ) -> dict:
        """Send notifications in batches for better performance.

        Args:
            user_batches: List of user batches
            promo: Flash promo to notify about

        Returns:
            Dictionary with batch notification results
        """
        total_results = {
            "total_batches": len(user_batches),
            "total_users": sum(len(batch) for batch in user_batches),
            "successful_notifications": 0,
            "failed_notifications": 0,
            "duplicate_notifications": 0,
        }

        for batch in user_batches:
            batch_results = self.send_flash_promo_notification(batch, promo)

            total_results["successful_notifications"] += batch_results[
                "successful_notifications"
            ]
            total_results["failed_notifications"] += batch_results[
                "failed_notifications"
            ]
            total_results["duplicate_notifications"] += batch_results[
                "duplicate_notifications"
            ]

        return total_results

    def clear_notification_history(self) -> None:
        """Clear notification history (useful for testing)."""
        self._sent_notifications.clear()
