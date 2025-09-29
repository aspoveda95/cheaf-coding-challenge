"""Reservation domain entity."""
# Standard Python Libraries
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4


class Reservation:
    """Reservation entity representing a product reservation."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        product_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        flash_promo_id: Optional[UUID] = None,
        store_id: Optional[UUID] = None,
        expires_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        """Initialize Reservation entity.

        Args:
            id: Unique identifier for the reservation
            product_id: ID of the reserved product
            user_id: ID of the user who made the reservation
            flash_promo_id: ID of the flash promo being used
            store_id: ID of the store where the product is sold
            expires_at: When the reservation expires
            created_at: When the reservation was created
        """
        self._id = id or uuid4()
        self._product_id = product_id
        self._user_id = user_id
        self._flash_promo_id = flash_promo_id
        self._store_id = store_id
        self._created_at = created_at or datetime.now()
        self._expires_at = expires_at or (self._created_at + timedelta(minutes=1))

    @property
    def id(self) -> UUID:
        """Get the reservation ID."""
        return self._id

    @property
    def product_id(self) -> Optional[UUID]:
        """Get the product ID."""
        return self._product_id

    @property
    def user_id(self) -> Optional[UUID]:
        """Get the user ID."""
        return self._user_id

    @property
    def flash_promo_id(self) -> Optional[UUID]:
        """Get the flash promo ID."""
        return self._flash_promo_id

    @property
    def store_id(self) -> Optional[UUID]:
        """Get the store ID."""
        return self._store_id

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        return self._created_at

    @property
    def expires_at(self) -> datetime:
        """Get the expiration timestamp."""
        return self._expires_at

    def is_expired(self, current_time: Optional[datetime] = None) -> bool:
        """Check if the reservation has expired."""
        if current_time is None:
            current_time = datetime.now()

        # Handle timezone-aware vs naive datetime comparison
        if self._expires_at.tzinfo is not None and current_time.tzinfo is None:
            # expires_at is timezone-aware, current_time is naive
            # Third-Party Libraries
            from django.utils import timezone

            current_time = timezone.now()
        elif self._expires_at.tzinfo is None and current_time.tzinfo is not None:
            # expires_at is naive, current_time is timezone-aware
            current_time = current_time.replace(tzinfo=None)

        return current_time >= self._expires_at

    def time_remaining_seconds(self, current_time: Optional[datetime] = None) -> int:
        """Get remaining time in seconds."""
        if current_time is None:
            current_time = datetime.now()

        # Handle timezone-aware vs naive datetime comparison
        if self._expires_at.tzinfo is not None and current_time.tzinfo is None:
            # expires_at is timezone-aware, current_time is naive
            # Third-Party Libraries
            from django.utils import timezone

            current_time = timezone.now()
        elif self._expires_at.tzinfo is None and current_time.tzinfo is not None:
            # expires_at is naive, current_time is timezone-aware
            current_time = current_time.replace(tzinfo=None)

        if self.is_expired(current_time):
            return 0

        delta = self._expires_at - current_time
        return int(delta.total_seconds())

    def extend_reservation(self, minutes: int = 1) -> None:
        """Extend the reservation by specified minutes."""
        self._expires_at += timedelta(minutes=minutes)

    def __str__(self) -> str:
        """Return string representation of Reservation."""
        return f"Reservation({self._id})"

    def __repr__(self) -> str:
        """Return detailed string representation of Reservation."""
        return f"Reservation(id={self._id}, product_id={self._product_id}, user_id={self._user_id})"

    def __eq__(self, other) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, Reservation):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash based on ID."""
        return hash(self._id)
