"""Store domain entity."""
# Standard Python Libraries
from typing import Optional
from uuid import UUID, uuid4

# Local Libraries
from src.domain.value_objects.location import Location


class Store:
    """Store entity representing a marketplace vendor."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        name: str = "",
        location: Optional[Location] = None,
        is_active: bool = True,
    ):
        """Initialize Store entity.

        Args:
            id: Unique identifier for the store
            name: Store name
            location: Store physical location
            is_active: Whether the store is active
        """
        self._id = id or uuid4()
        self._name = name
        self._location = location
        self._is_active = is_active

    @property
    def id(self) -> UUID:
        """Get the store ID."""
        return self._id

    @property
    def name(self) -> str:
        """Get the store name."""
        return self._name

    @property
    def location(self) -> Optional[Location]:
        """Get the store location."""
        return self._location

    @property
    def is_active(self) -> bool:
        """Check if the store is active."""
        return self._is_active

    def activate(self) -> None:
        """Activate the store."""
        self._is_active = True

    def deactivate(self) -> None:
        """Deactivate the store."""
        self._is_active = False

    def update_location(self, location: Location) -> None:
        """Update store location."""
        self._location = location

    def __str__(self) -> str:
        """Return string representation of Store."""
        return f"Store({self._name})"

    def __repr__(self) -> str:
        """Return detailed string representation of Store."""
        return f"Store(id={self._id}, name={self._name})"

    def __eq__(self, other) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, Store):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Return hash based on ID."""
        return hash(self._id)
