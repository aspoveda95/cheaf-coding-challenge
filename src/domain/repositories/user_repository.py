"""User repository interface."""
# Standard Python Libraries
from abc import ABC, abstractmethod
from typing import List, Optional, Set
from uuid import UUID

# Local Libraries
from src.domain.entities.user import User
from src.domain.value_objects.location import Location
from src.domain.value_objects.user_segment import UserSegment


class UserRepository(ABC):
    """Abstract repository for User entities."""

    @abstractmethod
    def save(self, user: User) -> User:
        """Save a user."""
        pass

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    def get_users_by_segments(self, segments: Set[UserSegment]) -> List[User]:
        """Get users by segments."""
        pass

    @abstractmethod
    def get_users_by_location(self, location: Location, radius_km: float) -> List[User]:
        """Get users within radius of location."""
        pass

    @abstractmethod
    def get_users_by_segments_and_location(
        self, segments: Set[UserSegment], location: Location, radius_km: float
    ) -> List[User]:
        """Get users by segments and location."""
        pass

    @abstractmethod
    def delete(self, user_id: UUID) -> bool:
        """Delete a user."""
        pass

    @abstractmethod
    def exists(self, user_id: UUID) -> bool:
        """Check if user exists."""
        pass
