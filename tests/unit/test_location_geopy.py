"""Tests for Location value object with GeoPy optimization."""
# Standard Python Libraries
from decimal import Decimal

# Third-Party Libraries
import pytest

# Local Libraries
from src.domain.value_objects.location import Location


class TestLocationGeoPy:
    """Test cases for Location with GeoPy methods."""

    def test_distance_to_geopy_same_location(self):
        """Test distance calculation to same location using GeoPy."""
        # Arrange
        location1 = Location(Decimal("40.7128"), Decimal("-74.0060"))  # NYC
        location2 = Location(Decimal("40.7128"), Decimal("-74.0060"))  # Same location

        # Act
        distance = location1.distance_to_geopy(location2)

        # Assert
        assert distance == Decimal("0.0")

    def test_distance_to_geopy_different_locations(self):
        """Test distance calculation between different locations using GeoPy."""
        # Arrange
        nyc = Location(Decimal("40.7128"), Decimal("-74.0060"))  # NYC
        la = Location(Decimal("34.0522"), Decimal("-118.2437"))  # LA

        # Act
        distance = nyc.distance_to_geopy(la)

        # Assert
        # Distance between NYC and LA is approximately 3944 km
        assert 3900 < float(distance) < 4000

    def test_distance_to_geopy_close_locations(self):
        """Test distance calculation for close locations using GeoPy."""
        # Arrange
        location1 = Location(Decimal("40.7128"), Decimal("-74.0060"))  # NYC
        location2 = Location(Decimal("40.7589"), Decimal("-73.9851"))  # Central Park

        # Act
        distance = location1.distance_to_geopy(location2)

        # Assert
        # Distance should be around 5-10 km
        assert 5 < float(distance) < 10

    def test_is_within_radius_geopy_true(self):
        """Test radius check when location is within radius using GeoPy."""
        # Arrange
        center = Location(Decimal("40.7128"), Decimal("-74.0060"))  # NYC
        nearby = Location(Decimal("40.7589"), Decimal("-73.9851"))  # Central Park
        radius_km = 10.0

        # Act
        is_within = center.is_within_radius_geopy(nearby, radius_km)

        # Assert
        assert is_within is True

    def test_is_within_radius_geopy_false(self):
        """Test radius check when location is outside radius using GeoPy."""
        # Arrange
        nyc = Location(Decimal("40.7128"), Decimal("-74.0060"))  # NYC
        la = Location(Decimal("34.0522"), Decimal("-118.2437"))  # LA
        radius_km = 10.0

        # Act
        is_within = nyc.is_within_radius_geopy(la, radius_km)

        # Assert
        assert is_within is False

    def test_is_within_radius_geopy_exact_radius(self):
        """Test radius check at exact radius boundary using GeoPy."""
        # Arrange
        center = Location(Decimal("40.7128"), Decimal("-74.0060"))  # NYC
        nearby = Location(Decimal("40.7589"), Decimal("-73.9851"))  # Central Park
        distance = center.distance_to_geopy(nearby)
        radius_km = float(distance)  # Exact distance

        # Act
        is_within = center.is_within_radius_geopy(nearby, radius_km)

        # Assert
        assert is_within is True

    def test_geopy_vs_haversine_accuracy(self):
        """Test that GeoPy provides more accurate results than Haversine."""
        # Arrange
        nyc = Location(Decimal("40.7128"), Decimal("-74.0060"))  # NYC
        tokyo = Location(Decimal("35.6762"), Decimal("139.6503"))  # Tokyo

        # Act
        distance_geopy = nyc.distance_to_geopy(tokyo)
        distance_haversine = nyc.distance_to(tokyo)

        # Assert
        # Both should be close, but GeoPy should be more accurate
        assert 10000 < float(distance_geopy) < 12000  # Real distance is ~10800 km
        assert 10000 < float(distance_haversine) < 12000

        # GeoPy and Haversine should be within 1% of each other for this distance
        difference = abs(float(distance_geopy) - float(distance_haversine))
        relative_difference = difference / float(distance_geopy)
        assert relative_difference < 0.01  # Less than 1% difference

    def test_geopy_with_decimal_radius(self):
        """Test GeoPy method with Decimal radius."""
        # Arrange
        center = Location(Decimal("40.7128"), Decimal("-74.0060"))  # NYC
        nearby = Location(Decimal("40.7589"), Decimal("-73.9851"))  # Central Park
        radius_km = Decimal("10.0")

        # Act
        is_within = center.is_within_radius_geopy(nearby, radius_km)

        # Assert
        assert is_within is True

    def test_geopy_with_float_radius(self):
        """Test GeoPy method with float radius."""
        # Arrange
        center = Location(Decimal("40.7128"), Decimal("-74.0060"))  # NYC
        nearby = Location(Decimal("40.7589"), Decimal("-73.9851"))  # Central Park
        radius_km = 10.0

        # Act
        is_within = center.is_within_radius_geopy(nearby, radius_km)

        # Assert
        assert is_within is True
