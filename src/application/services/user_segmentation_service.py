"""User segmentation service for Flash Promos."""
# Standard Python Libraries
from datetime import datetime, timedelta
from typing import List, Set
from uuid import UUID

# Local Libraries
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.location import Location
from src.domain.value_objects.user_segment import UserSegment


class UserSegmentationService:
    """Service for segmenting users based on behavior and location."""

    def __init__(self, user_repository: UserRepository):
        """Initialize UserSegmentationService with user repository."""
        self._user_repository = user_repository

    def segment_users_by_behavior(self, users: List[User]) -> dict:
        """Segment users based on their behavior patterns.

        Args:
            users: List of users to segment

        Returns:
            Dictionary with segments as keys and user lists as values
        """
        segments = {
            UserSegment.NEW_USERS: [],
            UserSegment.FREQUENT_BUYERS: [],
            UserSegment.VIP_CUSTOMERS: [],
            UserSegment.BEHAVIOR_BASED: [],
        }

        for user in users:
            if user.is_new_user():
                segments[UserSegment.NEW_USERS].append(user)

            if user.is_frequent_buyer():
                segments[UserSegment.FREQUENT_BUYERS].append(user)

            if user.is_vip_customer():
                segments[UserSegment.VIP_CUSTOMERS].append(user)

            segments[UserSegment.BEHAVIOR_BASED].append(user)

        return segments

    def get_users_by_segments(
        self, segments: Set[UserSegment], location: Location, radius_km: float = 2.0
    ) -> List[User]:
        """Get users by segments and location.

        Args:
            segments: Set of user segments to filter by
            location: Center location for radius filtering
            radius_km: Radius in kilometers

        Returns:
            List of users matching the criteria
        """
        return self._user_repository.get_users_by_segments_and_location(
            segments, location, radius_km
        )

    def get_users_within_radius(
        self, location: Location, radius_km: float = 2.0
    ) -> List[User]:
        """Get users within a specific radius of a location.

        Args:
            location: Center location
            radius_km: Radius in kilometers

        Returns:
            List of users within the radius
        """
        return self._user_repository.get_users_by_location(location, radius_km)

    def update_user_segments(self, user: User) -> User:
        """Update user segments based on current behavior.

        Args:
            user: User to update segments for

        Returns:
            Updated user with new segments
        """
        user_segments = set()

        if user.is_new_user():
            user_segments.add(UserSegment.NEW_USERS)

        if user.is_frequent_buyer():
            user_segments.add(UserSegment.FREQUENT_BUYERS)

        if user.is_vip_customer():
            user_segments.add(UserSegment.VIP_CUSTOMERS)

        for segment in user_segments:
            user.add_segment(segment)

        return self._user_repository.save(user)

    def get_segment_statistics(self, users: List[User]) -> dict:
        """Get statistics about user segments.

        Args:
            users: List of users to analyze

        Returns:
            Dictionary with segment statistics
        """
        stats = {
            "total_users": len(users),
            "new_users": 0,
            "frequent_buyers": 0,
            "vip_customers": 0,
            "users_with_location": 0,
        }

        for user in users:
            if user.is_new_user():
                stats["new_users"] += 1

            if user.is_frequent_buyer():
                stats["frequent_buyers"] += 1

            if user.is_vip_customer():
                stats["vip_customers"] += 1

            if user.location:
                stats["users_with_location"] += 1

        return stats
