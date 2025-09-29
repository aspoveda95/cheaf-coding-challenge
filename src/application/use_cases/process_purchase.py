"""Process Purchase use case."""
# Standard Python Libraries
from datetime import datetime
from typing import Optional
from uuid import UUID

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.reservation import Reservation
from src.domain.repositories.flash_promo_repository import FlashPromoRepository
from src.domain.repositories.reservation_repository import ReservationRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.price import Price


class ProcessPurchaseUseCase:
    """Use case for processing flash promo purchases."""

    def __init__(
        self,
        flash_promo_repository: FlashPromoRepository,
        reservation_repository: ReservationRepository,
        user_repository: UserRepository,
    ):
        """Initialize the use case with required repositories."""
        self._flash_promo_repository = flash_promo_repository
        self._reservation_repository = reservation_repository
        self._user_repository = user_repository

    def execute(self, reservation_id: UUID, user_id: UUID) -> bool:
        """Process a purchase for a reserved product.

        Args:
            reservation_id: ID of the reservation
            user_id: ID of the user making the purchase

        Returns:
            True if purchase was successful, False otherwise

        Raises:
            ValueError: If reservation not found or expired
        """
        reservation = self._reservation_repository.get_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")

        if reservation.user_id != user_id:
            raise ValueError("Reservation does not belong to this user")

        if reservation.is_expired():
            raise ValueError("Reservation has expired")

        flash_promo = self._flash_promo_repository.get_by_id(reservation.flash_promo_id)
        if not flash_promo:
            raise ValueError("Flash promo not found")

        if not flash_promo.is_currently_active():
            raise ValueError("Flash promo is no longer active")

        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        promo_price = flash_promo.promo_price
        if promo_price:
            user.record_purchase(float(promo_price.amount))
            self._user_repository.save(user)

        self._reservation_repository.delete(reservation_id)
        return True

    def get_purchase_price(self, reservation_id: UUID) -> Optional[Price]:
        """Get the purchase price for a reservation.

        Args:
            reservation_id: ID of the reservation

        Returns:
            Price if reservation is valid, None otherwise
        """
        reservation = self._reservation_repository.get_by_id(reservation_id)
        if not reservation or reservation.is_expired():
            return None

        flash_promo = self._flash_promo_repository.get_by_id(reservation.flash_promo_id)
        if not flash_promo or not flash_promo.is_currently_active():
            return None

        return flash_promo.promo_price
