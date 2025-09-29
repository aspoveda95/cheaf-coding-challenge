"""Email service interface."""
# Standard Python Libraries
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.user import User


class EmailService(ABC):
    """Abstract interface for email service implementations."""

    @abstractmethod
    def send_email(
        self, to_email: str, subject: str, message: str, user: Optional[User] = None
    ) -> bool:
        """Send email to a single recipient."""
        pass

    @abstractmethod
    def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        message: str,
        users: Optional[List[User]] = None,
    ) -> dict:
        """Send email to multiple recipients."""
        pass

    @abstractmethod
    def send_flash_promo_email(
        self, user: User, promo: FlashPromo, message: Optional[str] = None
    ) -> bool:
        """Send flash promo specific email."""
        pass

    @abstractmethod
    def send_bulk_flash_promo_email(
        self, users: List[User], promo: FlashPromo, message: Optional[str] = None
    ) -> dict:
        """Send flash promo emails to multiple users."""
        pass
