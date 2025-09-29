"""User domain entity."""
# Standard Python Libraries
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

# Local Libraries
from src.domain.value_objects.location import Location
from src.domain.value_objects.user_segment import UserSegment


class User:
    """User entity representing a marketplace customer."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        email: str = "",
        name: str = "",
        location: Optional[Location] = None,
        created_at: Optional[datetime] = None,
        last_purchase_at: Optional[datetime] = None,
        total_purchases: int = 0,
        total_spent: float = 0.0,
        segments: Optional[set] = None,
    ):
        """Initialize User entity.

        Args:
            id: Unique identifier for the user
            email: User email address
            name: User full name
            location: User current location
            created_at: Timestamp when the user was created
            last_purchase_at: Timestamp of last purchase
            total_purchases: Total number of purchases
            total_spent: Total amount spent
            segments: User behavioral segments
        """
        self._id = id or uuid4()
        self._email = email
        self._name = name
        self._location = location
        self._created_at = created_at or datetime.now()
        self._last_purchase_at = last_purchase_at
        self._total_purchases = total_purchases
        self._total_spent = total_spent
        self._segments = segments or set()

    @property
    def id(self) -> UUID:
        """Get the user ID."""
        return self._id

    @property
    def email(self) -> str:
        """Get the user email."""
        return self._email

    @property
    def name(self) -> str:
        """Get the user name."""
        return self._name

    @property
    def location(self) -> Optional[Location]:
        """Get the user location."""
        return self._location

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        return self._created_at

    @property
    def last_purchase_at(self) -> Optional[datetime]:
        """Get the last purchase timestamp."""
        return self._last_purchase_at

    @property
    def total_purchases(self) -> int:
        """Get the total number of purchases."""
        return self._total_purchases

    @property
    def total_spent(self) -> float:
        """Get the total amount spent."""
        return self._total_spent

    @property
    def segments(self) -> set:
        """Get the user segments."""
        return self._segments.copy()

    def is_new_user(self, days_threshold: int = 30) -> bool:
        """Check if user is considered new based on creation date."""
        days_since_creation = (datetime.now() - self._created_at).days
        return days_since_creation <= days_threshold

    def is_frequent_buyer(
        self, min_purchases: int = 5, days_threshold: int = 90
    ) -> bool:
        """Check if user is a frequent buyer."""
        if self._total_purchases < min_purchases:
            return False

        if not self._last_purchase_at:
            return False

        days_since_last_purchase = (datetime.now() - self._last_purchase_at).days
        return days_since_last_purchase <= days_threshold

    def is_vip_customer(self, min_spent: float = 1000.0) -> bool:
        """Check if user is VIP based on total spent."""
        return self._total_spent >= min_spent

    def add_segment(self, segment: UserSegment) -> None:
        """Add a user segment."""
        self._segments.add(segment)

    def remove_segment(self, segment: UserSegment) -> None:
        """Remove a user segment."""
        self._segments.discard(segment)

    def has_segment(self, segment: UserSegment) -> bool:
        """Check if user has a specific segment."""
        return segment in self._segments

    def update_location(self, location: Location) -> None:
        """Update user location."""
        self._location = location

    def record_purchase(self, amount: float) -> None:
        """Record a new purchase."""
        self._total_purchases += 1
        self._total_spent += amount
        self._last_purchase_at = datetime.now()

    def __str__(self) -> str:
        """Return string representation of User."""
        return f"User({self._email})"

    def __repr__(self) -> str:
        """Return detailed string representation of User."""
        return f"User(id={self._id}, email={self._email})"

    def __eq__(self, other) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, User):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash based on ID."""
        return hash(self._id)
