"""UserSegment value object."""
# Standard Python Libraries
from enum import Enum
from typing import List, Set


class UserSegment(Enum):
    """UserSegment enum representing user behavioral segments."""

    NEW_USERS = "new_users"
    FREQUENT_BUYERS = "frequent_buyers"
    VIP_CUSTOMERS = "vip_customers"
    LOCATION_BASED = "location_based"
    TIME_BASED = "time_based"
    BEHAVIOR_BASED = "behavior_based"

    def __str__(self) -> str:
        """Return string representation of UserSegment."""
        return self.value

    @classmethod
    def from_string(cls, segment_str: str) -> "UserSegment":
        """Create UserSegment from string."""
        try:
            return cls(segment_str)
        except ValueError:
            raise ValueError(f"Invalid user segment: {segment_str}")

    @classmethod
    def all_segments(cls) -> List["UserSegment"]:
        """Get all available segments."""
        return list(cls)

    @classmethod
    def from_strings(cls, segment_strings: List[str]) -> Set["UserSegment"]:
        """Create set of UserSegment from list of strings."""
        return {cls.from_string(seg) for seg in segment_strings}

    def get_display_name(self) -> str:
        """Get human-readable display name."""
        display_names = {
            UserSegment.NEW_USERS: "New Users",
            UserSegment.FREQUENT_BUYERS: "Frequent Buyers",
            UserSegment.VIP_CUSTOMERS: "VIP Customers",
            UserSegment.LOCATION_BASED: "Location Based",
            UserSegment.TIME_BASED: "Time Based",
            UserSegment.BEHAVIOR_BASED: "Behavior Based",
        }
        return display_names.get(self, self.value.title())
