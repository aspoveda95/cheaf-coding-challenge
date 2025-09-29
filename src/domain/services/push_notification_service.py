"""Push notification service interface."""
# Standard Python Libraries
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.user import User


class PushNotificationService(ABC):
    """Abstract interface for push notification service implementations."""

    @abstractmethod
    def send_push_notification(
        self, user: User, title: str, message: str, data: Optional[dict] = None
    ) -> bool:
        """Send push notification to a single user."""
        pass

    @abstractmethod
    def send_bulk_push_notification(
        self, users: List[User], title: str, message: str, data: Optional[dict] = None
    ) -> dict:
        """Send push notification to multiple users."""
        pass

    @abstractmethod
    def send_flash_promo_push(
        self, user: User, promo: FlashPromo, message: Optional[str] = None
    ) -> bool:
        """Send flash promo specific push notification."""
        pass

    @abstractmethod
    def send_bulk_flash_promo_push(
        self, users: List[User], promo: FlashPromo, message: Optional[str] = None
    ) -> dict:
        """Send flash promo push notifications to multiple users."""
        pass
