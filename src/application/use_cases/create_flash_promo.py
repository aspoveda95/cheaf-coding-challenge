"""Create Flash Promo use case."""
# Standard Python Libraries
from typing import Optional, Set
from uuid import UUID

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.product import Product
from src.domain.entities.store import Store
from src.domain.repositories.flash_promo_repository import FlashPromoRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.price import Price
from src.domain.value_objects.time_range import TimeRange
from src.domain.value_objects.user_segment import UserSegment


class CreateFlashPromoUseCase:
    """Use case for creating new flash promos."""

    def __init__(
        self,
        flash_promo_repository: FlashPromoRepository,
        user_repository: UserRepository,
    ):
        """Initialize the use case with required repositories."""
        self._flash_promo_repository = flash_promo_repository
        self._user_repository = user_repository

    def execute(
        self,
        product_id: UUID,
        store_id: UUID,
        promo_price: Price,
        time_range: TimeRange,
        user_segments: Set[UserSegment],
        max_radius_km: float = 2.0,
    ) -> FlashPromo:
        """Create a new flash promo.

        Args:
            product_id: ID of the product for the promo
            store_id: ID of the store offering the promo
            promo_price: Special price for the promo
            time_range: Time range when the promo is active
            user_segments: User segments eligible for the promo
            max_radius_km: Maximum radius in km for user eligibility

        Returns:
            Created FlashPromo entity

        Raises:
            ValueError: If validation fails
        """
        if max_radius_km < 0:
            raise ValueError("Max radius cannot be negative")

        if not user_segments:
            raise ValueError("At least one user segment must be specified")

        flash_promo = FlashPromo(
            product_id=product_id,
            store_id=store_id,
            promo_price=promo_price,
            time_range=time_range,
            user_segments=user_segments,
            max_radius_km=max_radius_km,
            # is_active defaults to False - promos must be activated manually
        )

        return self._flash_promo_repository.save(flash_promo)
