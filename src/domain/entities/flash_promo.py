"""Flash Promo domain entity."""
# Standard Python Libraries
from datetime import datetime
from typing import Optional, Set
from uuid import UUID, uuid4

# Local Libraries
from src.domain.value_objects.price import Price
from src.domain.value_objects.time_range import TimeRange
from src.domain.value_objects.user_segment import UserSegment


class FlashPromo:
    """Flash Promo entity representing a time-limited promotional offer."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        product_id: Optional[UUID] = None,
        store_id: Optional[UUID] = None,
        promo_price: Optional[Price] = None,
        time_range: Optional[TimeRange] = None,
        user_segments: Optional[Set[UserSegment]] = None,
        max_radius_km: float = 2.0,
        is_active: bool = False,
        created_at: Optional[datetime] = None,
    ):
        """Initialize Flash Promo entity.

        Args:
            id: Unique identifier for the flash promo
            product_id: ID of the product being promoted
            store_id: ID of the store offering the promo
            promo_price: Special promotional price
            time_range: Time window when promo is active
            user_segments: Target user segments for the promo
            max_radius_km: Maximum radius in km for location-based targeting
            is_active: Whether the promo is currently active
            created_at: Timestamp when the promo was created
        """
        self._id = id or uuid4()
        self._product_id = product_id
        self._store_id = store_id
        self._promo_price = promo_price
        self._time_range = time_range
        self._user_segments = user_segments or set()
        self._max_radius_km = max_radius_km
        self._is_active = is_active
        self._created_at = created_at or datetime.now()

    @property
    def id(self) -> UUID:
        """Get the flash promo ID."""
        return self._id

    @property
    def product_id(self) -> Optional[UUID]:
        """Get the product ID."""
        return self._product_id

    @property
    def store_id(self) -> Optional[UUID]:
        """Get the store ID."""
        return self._store_id

    @property
    def promo_price(self) -> Optional[Price]:
        """Get the promotional price."""
        return self._promo_price

    @property
    def time_range(self) -> Optional[TimeRange]:
        """Get the time range for the promo."""
        return self._time_range

    @property
    def user_segments(self) -> Set[UserSegment]:
        """Get the user segments for the promo."""
        return self._user_segments.copy()

    @property
    def max_radius_km(self) -> float:
        """Get the maximum radius in kilometers."""
        return self._max_radius_km

    @property
    def is_active(self) -> bool:
        """Check if the promo is active."""
        return self._is_active

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        return self._created_at

    def activate(self) -> None:
        """Activate the flash promo."""
        self._is_active = True

    def deactivate(self) -> None:
        """Deactivate the flash promo."""
        self._is_active = False

    def is_currently_active(self, current_time: Optional[datetime] = None) -> bool:
        """Check if the promo is currently active based on time and status."""
        if not self._is_active:
            return False

        if not self._time_range:
            return True

        return self._time_range.is_active_now(current_time)

    def is_eligible_for_user(self, user_segments: Set[UserSegment]) -> bool:
        """Check if user segments are eligible for this promo."""
        if not self._user_segments:
            return True

        return bool(self._user_segments.intersection(user_segments))

    def add_user_segment(self, segment: UserSegment) -> None:
        """Add a user segment to the promo."""
        self._user_segments.add(segment)

    def remove_user_segment(self, segment: UserSegment) -> None:
        """Remove a user segment from the promo."""
        self._user_segments.discard(segment)

    def update_time_range(self, time_range: TimeRange) -> None:
        """Update the time range for the promo."""
        self._time_range = time_range

    def update_promo_price(self, price: Price) -> None:
        """Update the promo price."""
        self._promo_price = price

    def update_radius(self, radius_km: float) -> None:
        """Update the maximum radius for the promo."""
        if radius_km < 0:
            raise ValueError("Radius cannot be negative")
        self._max_radius_km = radius_km

    def __str__(self) -> str:
        """Return string representation of FlashPromo."""
        return f"FlashPromo({self._id})"

    def __repr__(self) -> str:
        """Return detailed string representation of FlashPromo."""
        return f"FlashPromo(id={self._id}, product_id={self._product_id})"

    def __eq__(self, other) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, FlashPromo):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash based on ID."""
        return hash(self._id)
