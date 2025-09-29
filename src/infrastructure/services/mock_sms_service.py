# Standard Python Libraries
from typing import List, Optional
from uuid import UUID

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.user import User
from src.domain.services.sms_service import SMSService


class MockSMSService(SMSService):
    """Mock implementation of SMSService for development and testing."""

    def __init__(self):
        self._sent_sms = []

    def send_sms(
        self, phone_number: str, message: str, user: Optional[User] = None
    ) -> bool:
        """Send SMS to a single phone number (mock implementation)."""
        sms_data = {
            "phone_number": phone_number,
            "message": message,
            "user_id": str(user.id) if user else None,
            "timestamp": self._get_timestamp(),
        }

        self._sent_sms.append(sms_data)
        print(f"📱 [MOCK SMS] To: {phone_number}")
        print(f"   Message: {message}")
        print(f"   User ID: {user.id if user else 'N/A'}")
        print("   ✅ SMS sent successfully (mock)")
        print("-" * 50)

        return True

    def send_bulk_sms(
        self, phone_numbers: List[str], message: str, users: Optional[List[User]] = None
    ) -> dict:
        """Send SMS to multiple phone numbers (mock implementation)."""
        results = {
            "total_recipients": len(phone_numbers),
            "successful_sends": 0,
            "failed_sends": 0,
            "errors": [],
        }

        for i, phone in enumerate(phone_numbers):
            user = users[i] if users and i < len(users) else None
            try:
                if self.send_sms(phone, message, user):
                    results["successful_sends"] += 1
                else:
                    results["failed_sends"] += 1
                    results["errors"].append(f"Failed to send SMS to {phone}")
            except Exception as e:
                results["failed_sends"] += 1
                results["errors"].append(f"Error sending SMS to {phone}: {str(e)}")

        print(
            f"📱 [BULK SMS] Sent to {results['successful_sends']}/{results['total_recipients']} recipients"
        )
        return results

    def send_flash_promo_sms(
        self, user: User, promo: FlashPromo, message: Optional[str] = None
    ) -> bool:
        """Send flash promo specific SMS (mock implementation)."""
        if not message:
            message = self._generate_flash_promo_message(promo)

        return self.send_sms(phone_number=user.phone_number, message=message, user=user)

    def send_bulk_flash_promo_sms(
        self, users: List[User], promo: FlashPromo, message: Optional[str] = None
    ) -> dict:
        """Send flash promo SMS to multiple users (mock implementation)."""
        if not message:
            message = self._generate_flash_promo_message(promo)

        phone_numbers = [user.phone_number for user in users]

        return self.send_bulk_sms(
            phone_numbers=phone_numbers, message=message, users=users
        )

    def _generate_flash_promo_message(self, promo: FlashPromo) -> str:
        """Generate flash promo SMS message."""
        price_str = str(promo.promo_price) if promo.promo_price else "Special Price"

        return f"🔥 FLASH PROMO! {promo.product_name} at {price_str}. Limited time! Reply STOP to opt out."

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        # Standard Python Libraries
        from datetime import datetime

        return datetime.now().isoformat()

    def get_sent_sms(self) -> List[dict]:
        """Get list of sent SMS (for testing)."""
        return self._sent_sms.copy()

    def clear_sent_sms(self):
        """Clear sent SMS list (for testing)."""
        self._sent_sms.clear()
