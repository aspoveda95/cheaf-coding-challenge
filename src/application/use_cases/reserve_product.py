"""Reserve Product use case."""
# Standard Python Libraries
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.reservation import Reservation
from src.domain.repositories.flash_promo_repository import FlashPromoRepository
from src.domain.repositories.reservation_repository import ReservationRepository


class ReserveProductUseCase:
    """Use case for reserving products with flash promos."""

    def __init__(
        self,
        flash_promo_repository: FlashPromoRepository,
        reservation_repository: ReservationRepository,
    ):
        """Initialize the use case with required repositories."""
        self._flash_promo_repository = flash_promo_repository
        self._reservation_repository = reservation_repository

    def execute(
        self,
        product_id: UUID,
        user_id: UUID,
        flash_promo_id: UUID,
        reservation_duration_minutes: int = 1,
    ) -> Optional[Reservation]:
        """Reserve a product for a user during a flash promo.

        Args:
            product_id: ID of the product to reserve
            user_id: ID of the user making the reservation
            flash_promo_id: ID of the flash promo
            reservation_duration_minutes: Duration of reservation in minutes

        Returns:
            Reservation entity if successful, None if product already reserved

        Raises:
            ValueError: If flash promo not found or not active
        """
        flash_promo = self._flash_promo_repository.get_by_id(flash_promo_id)
        if not flash_promo:
            raise ValueError(f"Flash promo {flash_promo_id} not found")

        if not flash_promo.is_currently_active():
            raise ValueError(f"Flash promo {flash_promo_id} is not currently active")

        if self._reservation_repository.exists_active_for_product(product_id):
            return None

        expires_at = datetime.now() + timedelta(minutes=reservation_duration_minutes)

        reservation = Reservation(
            product_id=product_id,
            user_id=user_id,
            flash_promo_id=flash_promo_id,
            store_id=flash_promo.store_id,
            expires_at=expires_at,
        )

        return self._reservation_repository.save(reservation)

    def get_reservation(self, reservation_id: UUID) -> Optional[Reservation]:
        """Get a reservation by ID.

        Args:
            reservation_id: ID of the reservation

        Returns:
            Reservation entity if found, None otherwise
        """
        return self._reservation_repository.get_by_id(reservation_id)

    def is_product_reserved(self, product_id: UUID) -> bool:
        """Check if a product is currently reserved.

        Args:
            product_id: ID of the product to check

        Returns:
            True if product is reserved, False otherwise
        """
        return self._reservation_repository.exists_active_for_product(product_id)
