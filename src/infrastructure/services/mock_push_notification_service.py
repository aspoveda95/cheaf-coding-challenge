# Standard Python Libraries
from typing import Any, Dict, List, Optional
from uuid import UUID

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.user import User
from src.domain.services.push_notification_service import PushNotificationService


class MockPushNotificationService(PushNotificationService):
    """Mock implementation of PushNotificationService for development and testing."""

    def __init__(self):
        self._sent_notifications = []

    def send_push_notification(
        self, user: User, title: str, message: str, data: Optional[dict] = None
    ) -> bool:
        """Send push notification to a single user (mock implementation)."""
        notification_data = {
            "user_id": str(user.id),
            "title": title,
            "message": message,
            "data": data or {},
            "timestamp": self._get_timestamp(),
        }

        self._sent_notifications.append(notification_data)
        print(f"📱 [MOCK PUSH] To User: {user.id}")
        print(f"   Title: {title}")
        print(f"   Message: {message}")
        print(f"   Data: {data}")
        print("   ✅ Push notification sent successfully (mock)")
        print("-" * 50)

        return True

    def send_bulk_push_notification(
        self, users: List[User], title: str, message: str, data: Optional[dict] = None
    ) -> dict:
        """Send push notification to multiple users (mock implementation)."""
        results = {
            "total_users": len(users),
            "successful_sends": 0,
            "failed_sends": 0,
            "errors": [],
        }

        for user in users:
            try:
                if self.send_push_notification(user, title, message, data):
                    results["successful_sends"] += 1
                else:
                    results["failed_sends"] += 1
                    results["errors"].append(f"Failed to send push to user {user.id}")
            except Exception as e:
                results["failed_sends"] += 1
                results["errors"].append(
                    f"Error sending push to user {user.id}: {str(e)}"
                )

        print(
            f"📱 [BULK PUSH] Sent to {results['successful_sends']}/{results['total_users']} users"
        )
        return results

    def send_flash_promo_push(
        self, user: User, promo: FlashPromo, message: Optional[str] = None
    ) -> bool:
        """Send flash promo specific push notification (mock implementation)."""
        if not message:
            message = self._generate_flash_promo_message(promo)

        title = f"🔥 Product {promo.product_id} - Flash Promo!"

        data = {
            "promo_id": str(promo.id),
            "product_id": str(promo.product_id),
            "promo_price": str(promo.promo_price) if promo.promo_price else None,
            "type": "flash_promo",
        }

        return self.send_push_notification(
            user=user, title=title, message=message, data=data
        )

    def send_bulk_flash_promo_push(
        self, users: List[User], promo: FlashPromo, message: Optional[str] = None
    ) -> dict:
        """Send flash promo push notifications to multiple users (mock implementation)."""
        if not message:
            message = self._generate_flash_promo_message(promo)

        title = f"🔥 Product {promo.product_id} - Flash Promo!"

        data = {
            "promo_id": str(promo.id),
            "product_id": str(promo.product_id),
            "promo_price": str(promo.promo_price) if promo.promo_price else None,
            "type": "flash_promo",
        }

        return self.send_bulk_push_notification(
            users=users, title=title, message=message, data=data
        )

    def _generate_flash_promo_message(self, promo: FlashPromo) -> str:
        """Generate flash promo push message."""
        price_str = str(promo.promo_price) if promo.promo_price else "Special Price"

        return f"🔥 Flash Promo Alert! {promo.product_name} at {price_str}. Limited time offer!"

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        # Standard Python Libraries
        from datetime import datetime

        return datetime.now().isoformat()

    def get_sent_notifications(self) -> List[dict]:
        """Get list of sent notifications (for testing)."""
        return self._sent_notifications.copy()

    def clear_sent_notifications(self):
        """Clear sent notifications list (for testing)."""
        self._sent_notifications.clear()
