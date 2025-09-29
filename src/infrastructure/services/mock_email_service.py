# Standard Python Libraries
from typing import List, Optional
from uuid import UUID

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.user import User
from src.domain.services.email_service import EmailService


class MockEmailService(EmailService):
    """Mock implementation of EmailService for development and testing."""

    def __init__(self):
        self._sent_emails = []

    def send_email(
        self, to_email: str, subject: str, message: str, user: Optional[User] = None
    ) -> bool:
        """Send email to a single recipient (mock implementation)."""
        email_data = {
            "to": to_email,
            "subject": subject,
            "message": message,
            "user_id": str(user.id) if user else None,
            "timestamp": self._get_timestamp(),
        }

        self._sent_emails.append(email_data)
        print(f"📧 [MOCK EMAIL] To: {to_email}")
        print(f"   Subject: {subject}")
        print(f"   Message: {message[:100]}...")
        print(f"   User ID: {user.id if user else 'N/A'}")
        print("   ✅ Email sent successfully (mock)")
        print("-" * 50)

        return True

    def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        message: str,
        users: Optional[List[User]] = None,
    ) -> dict:
        """Send email to multiple recipients (mock implementation)."""
        results = {
            "total_recipients": len(recipients),
            "successful_sends": 0,
            "failed_sends": 0,
            "errors": [],
        }

        for i, email in enumerate(recipients):
            user = users[i] if users and i < len(users) else None
            try:
                if self.send_email(email, subject, message, user):
                    results["successful_sends"] += 1
                else:
                    results["failed_sends"] += 1
                    results["errors"].append(f"Failed to send to {email}")
            except Exception as e:
                results["failed_sends"] += 1
                results["errors"].append(f"Error sending to {email}: {str(e)}")

        print(
            f"📧 [BULK EMAIL] Sent to {results['successful_sends']}/{results['total_recipients']} recipients"
        )
        return results

    def send_flash_promo_email(
        self, user: User, promo: FlashPromo, message: Optional[str] = None
    ) -> bool:
        """Send flash promo specific email (mock implementation)."""
        if not message:
            message = self._generate_flash_promo_message(promo)

        subject = f"🔥 FLASH PROMO ALERT! - Product {promo.product_id}"

        return self.send_email(
            to_email=user.email, subject=subject, message=message, user=user
        )

    def send_bulk_flash_promo_email(
        self, users: List[User], promo: FlashPromo, message: Optional[str] = None
    ) -> dict:
        """Send flash promo emails to multiple users (mock implementation)."""
        if not message:
            message = self._generate_flash_promo_message(promo)

        subject = f"🔥 FLASH PROMO ALERT! - Product {promo.product_id}"
        emails = [user.email for user in users]

        return self.send_bulk_email(
            recipients=emails, subject=subject, message=message, users=users
        )

    def _generate_flash_promo_message(self, promo: FlashPromo) -> str:
        """Generate flash promo email message."""
        price_str = str(promo.promo_price) if promo.promo_price else "Special Price"
        time_str = str(promo.time_range) if promo.time_range else "Limited Time"

        return f"""
🔥 FLASH PROMO ALERT! 🔥

Product: {promo.product_id}
Special Price: {price_str}
Valid: {time_str}

Hurry up! This is a limited time offer!

Best regards,
Flash Promos Team
        """.strip()

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        # Standard Python Libraries
        from datetime import datetime

        return datetime.now().isoformat()

    def get_sent_emails(self) -> List[dict]:
        """Get list of sent emails (for testing)."""
        return self._sent_emails.copy()

    def clear_sent_emails(self):
        """Clear sent emails list (for testing)."""
        self._sent_emails.clear()
