# Standard Python Libraries
from datetime import time
from decimal import Decimal

# Third-Party Libraries
import pytest

# Local Libraries
from src.domain.value_objects.location import Location
from src.domain.value_objects.price import Price
from src.domain.value_objects.time_range import TimeRange
from src.domain.value_objects.user_segment import UserSegment


class TestPrice:
    """Test Price value object."""

    def test_price_creation(self):
        """Test price creation with different types."""
        # From Decimal
        price1 = Price(Decimal("99.99"))
        assert price1.amount == Decimal("99.99")

        # From float
        price2 = Price(50.0)
        assert price2.amount == Decimal("50.0")

        # From string
        price3 = Price("25.50")
        assert price3.amount == Decimal("25.50")

    def test_price_negative_validation(self):
        """Test price validation for negative values."""
        with pytest.raises(ValueError, match="Price cannot be negative"):
            Price(-10.0)

    def test_price_comparison(self):
        """Test price comparison operations."""
        price1 = Price(Decimal("50.00"))
        price2 = Price(Decimal("100.00"))
        price3 = Price(Decimal("50.00"))

        assert price1 < price2
        assert price1 <= price2
        assert price2 > price1
        assert price2 >= price1
        assert price1 == price3
        assert price1 != price2

    def test_price_arithmetic(self):
        """Test price arithmetic operations."""
        price1 = Price(Decimal("50.00"))
        price2 = Price(Decimal("25.00"))

        # Addition
        sum_price = price1 + price2
        assert sum_price.amount == Decimal("75.00")

        # Subtraction
        diff_price = price1 - price2
        assert diff_price.amount == Decimal("25.00")

        # Multiplication
        mult_price = price1 * 2
        assert mult_price.amount == Decimal("100.00")

        # Division
        div_price = price1 / 2
        assert div_price.amount == Decimal("25.00")

    def test_price_discount_calculation(self):
        """Test discount percentage calculation."""
        original_price = Price(Decimal("100.00"))
        discounted_price = Price(Decimal("80.00"))

        discount_percentage = discounted_price.calculate_discount_percentage(
            original_price
        )
        assert discount_percentage == Decimal("20.00")

    def test_price_string_representation(self):
        """Test price string representation."""
        price = Price(Decimal("99.99"))
        assert str(price) == "$99.99"
        assert "Price(99.99)" in repr(price)


class TestLocation:
    """Test Location value object."""

    def test_location_creation(self):
        """Test location creation with different types."""
        # From Decimal
        location1 = Location(Decimal("40.7128"), Decimal("-74.0060"))
        assert location1.latitude == Decimal("40.7128")
        assert location1.longitude == Decimal("-74.0060")

        # From float
        location2 = Location(40.7128, -74.0060)
        assert location2.latitude == Decimal("40.7128")
        assert location2.longitude == Decimal("-74.0060")

        # From string
        location3 = Location("40.7128", "-74.0060")
        assert location3.latitude == Decimal("40.7128")
        assert location3.longitude == Decimal("-74.0060")

    def test_location_validation(self):
        """Test location coordinate validation."""
        # Valid coordinates
        valid_location = Location(40.7128, -74.0060)
        assert valid_location.latitude == Decimal("40.7128")
        assert valid_location.longitude == Decimal("-74.0060")

        # Invalid latitude
        with pytest.raises(
            ValueError, match="Latitude must be between -90 and 90 degrees"
        ):
            Location(91.0, -74.0060)

        # Invalid longitude
        with pytest.raises(
            ValueError, match="Longitude must be between -180 and 180 degrees"
        ):
            Location(40.7128, 181.0)

    def test_location_distance_calculation(self):
        """Test distance calculation between locations."""
        # NYC coordinates
        nyc = Location(Decimal("40.7128"), Decimal("-74.0060"))
        # Times Square (close to NYC)
        times_square = Location(Decimal("40.7589"), Decimal("-73.9851"))

        distance = nyc.distance_to(times_square)
        assert distance > 0
        assert distance < 10  # Should be less than 10 km

    def test_location_radius_check(self):
        """Test radius checking."""
        center = Location(Decimal("40.7128"), Decimal("-74.0060"))
        nearby = Location(Decimal("40.7130"), Decimal("-74.0058"))
        far_away = Location(Decimal("40.8000"), Decimal("-73.9000"))

        # Within radius
        assert center.is_within_radius(nearby, 1.0)  # 1 km radius

        # Outside radius
        assert not center.is_within_radius(far_away, 1.0)  # 1 km radius

    def test_location_equality(self):
        """Test location equality."""
        location1 = Location(Decimal("40.7128"), Decimal("-74.0060"))
        location2 = Location(Decimal("40.7128"), Decimal("-74.0060"))
        location3 = Location(Decimal("40.7130"), Decimal("-74.0060"))

        assert location1 == location2
        assert location1 != location3

    def test_location_string_representation(self):
        """Test location string representation."""
        location = Location(Decimal("40.7128"), Decimal("-74.0060"))
        assert str(location) == "(40.7128, -74.0060)"
        assert "Location(40.7128, -74.0060)" in repr(location)


class TestTimeRange:
    """Test TimeRange value object."""

    def test_time_range_creation(self):
        """Test time range creation."""
        start_time = time(9, 0)  # 9:00 AM
        end_time = time(17, 0)  # 5:00 PM
        time_range = TimeRange(start_time, end_time)

        assert time_range.start_time == start_time
        assert time_range.end_time == end_time

    def test_time_range_validation(self):
        """Test time range validation."""
        start_time = time(9, 0)
        end_time = time(17, 0)

        # Valid time range
        valid_range = TimeRange(start_time, end_time)
        assert valid_range.start_time == start_time
        assert valid_range.end_time == end_time

        # Invalid time range (start >= end)
        with pytest.raises(ValueError, match="Start time must be before end time"):
            TimeRange(end_time, start_time)

    def test_time_range_active_check(self):
        """Test time range active status checking."""
        # Morning range (9 AM to 12 PM)
        morning_range = TimeRange(time(9, 0), time(12, 0))

        # Test with different times
        morning_time = time(10, 30)
        afternoon_time = time(14, 0)

        assert morning_range.is_active_at(morning_time)
        assert not morning_range.is_active_at(afternoon_time)

    def test_time_range_duration(self):
        """Test time range duration calculation."""
        # 8-hour range
        time_range = TimeRange(time(9, 0), time(17, 0))
        assert time_range.duration_minutes() == 480  # 8 hours = 480 minutes

        # 1-hour range
        short_range = TimeRange(time(14, 0), time(15, 0))
        assert short_range.duration_minutes() == 60  # 1 hour = 60 minutes

    def test_time_range_equality(self):
        """Test time range equality."""
        time_range1 = TimeRange(time(9, 0), time(17, 0))
        time_range2 = TimeRange(time(9, 0), time(17, 0))
        time_range3 = TimeRange(time(10, 0), time(18, 0))

        assert time_range1 == time_range2
        assert time_range1 != time_range3

    def test_time_range_string_representation(self):
        """Test time range string representation."""
        time_range = TimeRange(time(9, 0), time(17, 0))
        assert str(time_range) == "09:00:00 - 17:00:00"
        assert "TimeRange(09:00:00, 17:00:00)" in repr(time_range)


class TestUserSegment:
    """Test UserSegment value object."""

    def test_user_segment_enum_values(self):
        """Test user segment enum values."""
        assert UserSegment.NEW_USERS.value == "new_users"
        assert UserSegment.FREQUENT_BUYERS.value == "frequent_buyers"
        assert UserSegment.VIP_CUSTOMERS.value == "vip_customers"
        assert UserSegment.LOCATION_BASED.value == "location_based"
        assert UserSegment.TIME_BASED.value == "time_based"
        assert UserSegment.BEHAVIOR_BASED.value == "behavior_based"

    def test_user_segment_from_string(self):
        """Test creating user segment from string."""
        segment = UserSegment.from_string("new_users")
        assert segment == UserSegment.NEW_USERS

        segment = UserSegment.from_string("frequent_buyers")
        assert segment == UserSegment.FREQUENT_BUYERS

    def test_user_segment_invalid_string(self):
        """Test creating user segment from invalid string."""
        with pytest.raises(ValueError, match="Invalid user segment: invalid_segment"):
            UserSegment.from_string("invalid_segment")

    def test_user_segment_from_strings(self):
        """Test creating multiple segments from strings."""
        segment_strings = ["new_users", "frequent_buyers", "vip_customers"]
        segments = UserSegment.from_strings(segment_strings)

        expected_segments = {
            UserSegment.NEW_USERS,
            UserSegment.FREQUENT_BUYERS,
            UserSegment.VIP_CUSTOMERS,
        }
        assert segments == expected_segments

    def test_user_segment_all_segments(self):
        """Test getting all available segments."""
        all_segments = UserSegment.all_segments()
        assert len(all_segments) == 6
        assert UserSegment.NEW_USERS in all_segments
        assert UserSegment.FREQUENT_BUYERS in all_segments
        assert UserSegment.VIP_CUSTOMERS in all_segments
        assert UserSegment.LOCATION_BASED in all_segments
        assert UserSegment.TIME_BASED in all_segments
        assert UserSegment.BEHAVIOR_BASED in all_segments

    def test_user_segment_display_name(self):
        """Test user segment display names."""
        assert UserSegment.NEW_USERS.get_display_name() == "New Users"
        assert UserSegment.FREQUENT_BUYERS.get_display_name() == "Frequent Buyers"
        assert UserSegment.VIP_CUSTOMERS.get_display_name() == "VIP Customers"
        assert UserSegment.LOCATION_BASED.get_display_name() == "Location Based"
        assert UserSegment.TIME_BASED.get_display_name() == "Time Based"
        assert UserSegment.BEHAVIOR_BASED.get_display_name() == "Behavior Based"

    def test_user_segment_string_representation(self):
        """Test user segment string representation."""
        segment = UserSegment.NEW_USERS
        assert str(segment) == "new_users"
