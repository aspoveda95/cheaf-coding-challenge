"""Location value object."""
# Standard Python Libraries
from decimal import Decimal
import math
from typing import Union

# Third-Party Libraries
from geopy.distance import geodesic


class Location:
    """Location value object representing geographic coordinates."""

    def __init__(
        self,
        latitude: Union[Decimal, float, str],
        longitude: Union[Decimal, float, str],
    ):
        """Initialize Location value object.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        """
        if isinstance(latitude, str):
            latitude = Decimal(latitude)
        elif isinstance(latitude, float):
            latitude = Decimal(str(latitude))

        if isinstance(longitude, str):
            longitude = Decimal(longitude)
        elif isinstance(longitude, float):
            longitude = Decimal(str(longitude))

        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees")

        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees")

        self._latitude = latitude
        self._longitude = longitude

    @property
    def latitude(self) -> Decimal:
        """Get the latitude coordinate."""
        return self._latitude

    @property
    def longitude(self) -> Decimal:
        """Get the longitude coordinate."""
        return self._longitude

    def distance_to(self, other: "Location") -> Decimal:
        """Calculate distance between two locations using Haversine formula.

        Returns distance in kilometers.
        """
        if not isinstance(other, Location):
            raise ValueError("Other must be a Location instance")

        # Convert to radians
        lat1_rad = math.radians(float(self._latitude))
        lon1_rad = math.radians(float(self._longitude))
        lat2_rad = math.radians(float(other._latitude))
        lon2_rad = math.radians(float(other._longitude))

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # Earth's radius in kilometers
        earth_radius = 6371

        return Decimal(str(c * earth_radius))

    def is_within_radius(
        self, other: "Location", radius_km: Union[Decimal, float]
    ) -> bool:
        """Check if another location is within the specified radius."""
        if isinstance(radius_km, float):
            radius_km = Decimal(str(radius_km))

        return self.distance_to(other) <= radius_km

    def distance_to_geopy(self, other: "Location") -> Decimal:
        """Calculate distance using GeoPy geodesic method (more accurate)."""
        if not isinstance(other, Location):
            raise ValueError("Other must be a Location instance")

        # Convert to tuples for geopy
        point1 = (float(self._latitude), float(self._longitude))
        point2 = (float(other._latitude), float(other._longitude))

        # Use geodesic distance (more accurate than Haversine)
        distance_km = geodesic(point1, point2).kilometers
        return Decimal(str(distance_km))

    def is_within_radius_geopy(
        self, other: "Location", radius_km: Union[Decimal, float]
    ) -> bool:
        """Check if another location is within radius using GeoPy (more accurate)."""
        if isinstance(radius_km, float):
            radius_km = Decimal(str(radius_km))

        return self.distance_to_geopy(other) <= radius_km

    def __str__(self) -> str:
        """Return string representation of Location."""
        return f"({self._latitude}, {self._longitude})"

    def __repr__(self) -> str:
        """Return detailed string representation of Location."""
        return f"Location({self._latitude}, {self._longitude})"

    def __eq__(self, other) -> bool:
        """Check equality based on coordinates."""
        if not isinstance(other, Location):
            return False
        return self._latitude == other._latitude and self._longitude == other._longitude

    def __hash__(self) -> int:
        """Return hash based on coordinates."""
        return hash((self._latitude, self._longitude))
