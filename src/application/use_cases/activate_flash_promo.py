"""Activate Flash Promo use case."""
# Standard Python Libraries
from datetime import datetime
from typing import List
from uuid import UUID

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.user import User
from src.domain.repositories.flash_promo_repository import FlashPromoRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.user_segment import UserSegment


class ActivateFlashPromoUseCase:
    """Use case for activating flash promos and notifying users."""

    def __init__(
        self,
        flash_promo_repository: FlashPromoRepository,
        user_repository: UserRepository,
    ):
        """Initialize the use case with required repositories."""
        self._flash_promo_repository = flash_promo_repository
        self._user_repository = user_repository

    def execute(self, promo_id: UUID) -> FlashPromo:
        """Activate a flash promo.

        Args:
            promo_id: ID of the promo to activate

        Returns:
            Activated FlashPromo entity

        Raises:
            ValueError: If promo not found
        """
        flash_promo = self._flash_promo_repository.get_by_id(promo_id)
        if not flash_promo:
            raise ValueError(f"Flash promo {promo_id} not found")

        flash_promo.activate()
        return self._flash_promo_repository.save(flash_promo)

    def get_active_promos(self, current_time: datetime = None) -> List[FlashPromo]:
        """Get all currently active flash promos.

        Args:
            current_time: Time to check against (defaults to now)

        Returns:
            List of active FlashPromo entities
        """
        # For global API, return all promos marked as active
        # Time-based filtering should be handled by the client or specific endpoints
        return self._flash_promo_repository.get_active_promos()

    def get_eligible_users_for_promo(self, promo_id: UUID) -> List[User]:
        """Get users eligible for a specific flash promo.

        Args:
            promo_id: ID of the flash promo

        Returns:
            List of eligible User entities
        """
        flash_promo = self._flash_promo_repository.get_by_id(promo_id)
        if not flash_promo:
            return []

        if not flash_promo.is_currently_active():
            return []

        return self._user_repository.get_users_by_segments(flash_promo.user_segments)
