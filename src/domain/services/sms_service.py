"""SMS service interface."""
# Standard Python Libraries
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.user import User


class SMSService(ABC):
    """Abstract interface for SMS service implementations."""

    @abstractmethod
    def send_sms(
        self, phone_number: str, message: str, user: Optional[User] = None
    ) -> bool:
        """Send SMS to a single phone number."""
        pass

    @abstractmethod
    def send_bulk_sms(
        self, phone_numbers: List[str], message: str, users: Optional[List[User]] = None
    ) -> dict:
        """Send SMS to multiple phone numbers."""
        pass

    @abstractmethod
    def send_flash_promo_sms(
        self, user: User, promo: FlashPromo, message: Optional[str] = None
    ) -> bool:
        """Send flash promo specific SMS."""
        pass

    @abstractmethod
    def send_bulk_flash_promo_sms(
        self, users: List[User], promo: FlashPromo, message: Optional[str] = None
    ) -> dict:
        """Send flash promo SMS to multiple users."""
        pass
