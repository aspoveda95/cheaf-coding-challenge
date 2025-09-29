"""Tests for UserSegmentationService."""
# Standard Python Libraries
from datetime import datetime, timedelta
from unittest.mock import Mock
from uuid import uuid4

# Third-Party Libraries
import pytest

# Local Libraries
from src.application.services.user_segmentation_service import UserSegmentationService
from src.domain.entities.user import User
from src.domain.value_objects.location import Location
from src.domain.value_objects.user_segment import UserSegment


class TestUserSegmentationService:
    """Test cases for UserSegmentationService."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock repository
        self.mock_user_repo = Mock()

        # Create service instance
        self.service = UserSegmentationService(self.mock_user_repo)

        # Create test data
        self.location = Location(40.7128, -74.0060)

        self.new_user = User(
            id=uuid4(),
            email="new@example.com",
            name="New User",
            location=self.location,
            created_at=datetime.now() - timedelta(days=1),  # Recent user
            total_purchases=0,
            total_spent=0.0,
        )

        self.frequent_buyer = User(
            id=uuid4(),
            email="frequent@example.com",
            name="Frequent Buyer",
            location=self.location,
            created_at=datetime.now() - timedelta(days=60),  # Not new user
            total_purchases=15,
            total_spent=500.0,
            last_purchase_at=datetime.now() - timedelta(days=5),  # Recent purchase
        )

        self.vip_customer = User(
            id=uuid4(),
            email="vip@example.com",
            name="VIP Customer",
            location=self.location,
            created_at=datetime.now() - timedelta(days=60),
            total_purchases=50,
            total_spent=2000.0,
            last_purchase_at=datetime.now() - timedelta(days=10),  # Recent purchase
        )

        self.user_without_location = User(
            id=uuid4(),
            email="nolocation@example.com",
            name="No Location User",
            location=None,
            created_at=datetime.now() - timedelta(days=45),  # Not new user
            total_purchases=2,  # Not frequent buyer
            total_spent=50.0,
            last_purchase_at=datetime.now() - timedelta(days=20),  # Recent purchase
        )

    def test_segment_users_by_behavior_new_users(self):
        """Test segmenting users by behavior - new users."""
        # Arrange
        users = [self.new_user, self.frequent_buyer, self.vip_customer]

        # Act
        result = self.service.segment_users_by_behavior(users)

        # Assert
        assert len(result[UserSegment.NEW_USERS]) == 1
        assert self.new_user in result[UserSegment.NEW_USERS]
        assert self.frequent_buyer not in result[UserSegment.NEW_USERS]
        assert self.vip_customer not in result[UserSegment.NEW_USERS]

    def test_segment_users_by_behavior_frequent_buyers(self):
        """Test segmenting users by behavior - frequent buyers."""
        # Arrange
        users = [self.new_user, self.frequent_buyer, self.vip_customer]

        # Act
        result = self.service.segment_users_by_behavior(users)

        # Assert
        assert (
            len(result[UserSegment.FREQUENT_BUYERS]) == 2
        )  # frequent_buyer and vip_customer
        assert self.new_user not in result[UserSegment.FREQUENT_BUYERS]
        assert self.frequent_buyer in result[UserSegment.FREQUENT_BUYERS]
        assert self.vip_customer in result[UserSegment.FREQUENT_BUYERS]

    def test_segment_users_by_behavior_vip_customers(self):
        """Test segmenting users by behavior - VIP customers."""
        # Arrange
        users = [self.new_user, self.frequent_buyer, self.vip_customer]

        # Act
        result = self.service.segment_users_by_behavior(users)

        # Assert
        assert len(result[UserSegment.VIP_CUSTOMERS]) == 1
        assert self.new_user not in result[UserSegment.VIP_CUSTOMERS]
        assert self.frequent_buyer not in result[UserSegment.VIP_CUSTOMERS]
        assert self.vip_customer in result[UserSegment.VIP_CUSTOMERS]

    def test_segment_users_by_behavior_behavior_based(self):
        """Test segmenting users by behavior - behavior based (all users)."""
        # Arrange
        users = [self.new_user, self.frequent_buyer, self.vip_customer]

        # Act
        result = self.service.segment_users_by_behavior(users)

        # Assert
        assert len(result[UserSegment.BEHAVIOR_BASED]) == 3
        assert self.new_user in result[UserSegment.BEHAVIOR_BASED]
        assert self.frequent_buyer in result[UserSegment.BEHAVIOR_BASED]
        assert self.vip_customer in result[UserSegment.BEHAVIOR_BASED]

    def test_segment_users_by_behavior_empty_list(self):
        """Test segmenting users by behavior with empty list."""
        # Arrange
        users = []

        # Act
        result = self.service.segment_users_by_behavior(users)

        # Assert
        assert len(result[UserSegment.NEW_USERS]) == 0
        assert len(result[UserSegment.FREQUENT_BUYERS]) == 0
        assert len(result[UserSegment.VIP_CUSTOMERS]) == 0
        assert len(result[UserSegment.BEHAVIOR_BASED]) == 0

    def test_get_users_by_segments_with_location(self):
        """Test getting users by segments with location."""
        # Arrange
        segments = {UserSegment.NEW_USERS, UserSegment.FREQUENT_BUYERS}
        radius_km = 5.0
        expected_users = [self.new_user, self.frequent_buyer]
        self.mock_user_repo.get_users_by_segments_and_location.return_value = (
            expected_users
        )

        # Act
        result = self.service.get_users_by_segments(segments, self.location, radius_km)

        # Assert
        assert result == expected_users
        self.mock_user_repo.get_users_by_segments_and_location.assert_called_once_with(
            segments, self.location, radius_km
        )

    def test_get_users_by_segments_default_radius(self):
        """Test getting users by segments with default radius."""
        # Arrange
        segments = {UserSegment.NEW_USERS}
        expected_users = [self.new_user]
        self.mock_user_repo.get_users_by_segments_and_location.return_value = (
            expected_users
        )

        # Act
        result = self.service.get_users_by_segments(segments, self.location)

        # Assert
        assert result == expected_users
        self.mock_user_repo.get_users_by_segments_and_location.assert_called_once_with(
            segments, self.location, 2.0
        )

    def test_get_users_by_segments_empty_result(self):
        """Test getting users by segments with empty result."""
        # Arrange
        segments = {UserSegment.NEW_USERS}
        self.mock_user_repo.get_users_by_segments_and_location.return_value = []

        # Act
        result = self.service.get_users_by_segments(segments, self.location)

        # Assert
        assert result == []
        self.mock_user_repo.get_users_by_segments_and_location.assert_called_once_with(
            segments, self.location, 2.0
        )

    def test_get_users_within_radius(self):
        """Test getting users within radius."""
        # Arrange
        radius_km = 10.0
        expected_users = [self.new_user, self.frequent_buyer, self.vip_customer]
        self.mock_user_repo.get_users_by_location.return_value = expected_users

        # Act
        result = self.service.get_users_within_radius(self.location, radius_km)

        # Assert
        assert result == expected_users
        self.mock_user_repo.get_users_by_location.assert_called_once_with(
            self.location, radius_km
        )

    def test_get_users_within_radius_default_radius(self):
        """Test getting users within radius with default radius."""
        # Arrange
        expected_users = [self.new_user, self.frequent_buyer]
        self.mock_user_repo.get_users_by_location.return_value = expected_users

        # Act
        result = self.service.get_users_within_radius(self.location)

        # Assert
        assert result == expected_users
        self.mock_user_repo.get_users_by_location.assert_called_once_with(
            self.location, 2.0
        )

    def test_get_users_within_radius_empty_result(self):
        """Test getting users within radius with empty result."""
        # Arrange
        self.mock_user_repo.get_users_by_location.return_value = []

        # Act
        result = self.service.get_users_within_radius(self.location)

        # Assert
        assert result == []
        self.mock_user_repo.get_users_by_location.assert_called_once_with(
            self.location, 2.0
        )

    def test_update_user_segments_new_user(self):
        """Test updating user segments for new user."""
        # Arrange
        user = self.new_user
        self.mock_user_repo.save.return_value = user

        # Act
        result = self.service.update_user_segments(user)

        # Assert
        assert result == user
        self.mock_user_repo.save.assert_called_once_with(user)

    def test_update_user_segments_frequent_buyer(self):
        """Test updating user segments for frequent buyer."""
        # Arrange
        user = self.frequent_buyer
        self.mock_user_repo.save.return_value = user

        # Act
        result = self.service.update_user_segments(user)

        # Assert
        assert result == user
        self.mock_user_repo.save.assert_called_once_with(user)

    def test_update_user_segments_vip_customer(self):
        """Test updating user segments for VIP customer."""
        # Arrange
        user = self.vip_customer
        self.mock_user_repo.save.return_value = user

        # Act
        result = self.service.update_user_segments(user)

        # Assert
        assert result == user
        self.mock_user_repo.save.assert_called_once_with(user)

    def test_update_user_segments_user_without_segments(self):
        """Test updating user segments for user without any segments."""
        # Arrange
        user = User(
            id=uuid4(),
            email="test@example.com",
            name="Test User",
            location=self.location,
            created_at=datetime.now() - timedelta(days=15),
            total_purchases=2,
            total_spent=50.0,
        )
        self.mock_user_repo.save.return_value = user

        # Act
        result = self.service.update_user_segments(user)

        # Assert
        assert result == user
        self.mock_user_repo.save.assert_called_once_with(user)

    def test_get_segment_statistics_complete_data(self):
        """Test getting segment statistics with complete data."""
        # Arrange
        users = [
            self.new_user,
            self.frequent_buyer,
            self.vip_customer,
            self.user_without_location,
        ]

        # Act
        result = self.service.get_segment_statistics(users)

        # Assert
        assert result["total_users"] == 4
        assert result["new_users"] == 1
        assert result["frequent_buyers"] == 2  # frequent_buyer and vip_customer
        assert result["vip_customers"] == 1
        assert result["users_with_location"] == 3  # All except user_without_location

    def test_get_segment_statistics_empty_list(self):
        """Test getting segment statistics with empty list."""
        # Arrange
        users = []

        # Act
        result = self.service.get_segment_statistics(users)

        # Assert
        assert result["total_users"] == 0
        assert result["new_users"] == 0
        assert result["frequent_buyers"] == 0
        assert result["vip_customers"] == 0
        assert result["users_with_location"] == 0

    def test_get_segment_statistics_only_new_users(self):
        """Test getting segment statistics with only new users."""
        # Arrange
        users = [self.new_user]

        # Act
        result = self.service.get_segment_statistics(users)

        # Assert
        assert result["total_users"] == 1
        assert result["new_users"] == 1
        assert result["frequent_buyers"] == 0
        assert result["vip_customers"] == 0
        assert result["users_with_location"] == 1

    def test_get_segment_statistics_only_frequent_buyers(self):
        """Test getting segment statistics with only frequent buyers."""
        # Arrange
        users = [self.frequent_buyer]

        # Act
        result = self.service.get_segment_statistics(users)

        # Assert
        assert result["total_users"] == 1
        assert result["new_users"] == 0
        assert result["frequent_buyers"] == 1
        assert result["vip_customers"] == 0
        assert result["users_with_location"] == 1

    def test_get_segment_statistics_only_vip_customers(self):
        """Test getting segment statistics with only VIP customers."""
        # Arrange
        users = [self.vip_customer]

        # Act
        result = self.service.get_segment_statistics(users)

        # Assert
        assert result["total_users"] == 1
        assert result["new_users"] == 0
        assert result["frequent_buyers"] == 1  # VIP customers are also frequent buyers
        assert result["vip_customers"] == 1
        assert result["users_with_location"] == 1

    def test_get_segment_statistics_users_without_location(self):
        """Test getting segment statistics with users without location."""
        # Arrange
        users = [self.user_without_location]

        # Act
        result = self.service.get_segment_statistics(users)

        # Assert
        assert result["total_users"] == 1
        assert result["new_users"] == 0
        assert result["frequent_buyers"] == 0
        assert result["vip_customers"] == 0
        assert result["users_with_location"] == 0

    def test_segment_users_by_behavior_mixed_segments(self):
        """Test segmenting users by behavior with mixed segments."""
        # Arrange
        users = [
            self.new_user,
            self.frequent_buyer,
            self.vip_customer,
            self.user_without_location,
        ]

        # Act
        result = self.service.segment_users_by_behavior(users)

        # Assert
        assert len(result[UserSegment.NEW_USERS]) == 1
        assert len(result[UserSegment.FREQUENT_BUYERS]) == 2
        assert len(result[UserSegment.VIP_CUSTOMERS]) == 1
        assert len(result[UserSegment.BEHAVIOR_BASED]) == 4

    def test_get_users_by_segments_single_segment(self):
        """Test getting users by segments with single segment."""
        # Arrange
        segments = {UserSegment.NEW_USERS}
        expected_users = [self.new_user]
        self.mock_user_repo.get_users_by_segments_and_location.return_value = (
            expected_users
        )

        # Act
        result = self.service.get_users_by_segments(segments, self.location)

        # Assert
        assert result == expected_users
        self.mock_user_repo.get_users_by_segments_and_location.assert_called_once_with(
            segments, self.location, 2.0
        )

    def test_get_users_by_segments_multiple_segments(self):
        """Test getting users by segments with multiple segments."""
        # Arrange
        segments = {
            UserSegment.NEW_USERS,
            UserSegment.FREQUENT_BUYERS,
            UserSegment.VIP_CUSTOMERS,
        }
        expected_users = [self.new_user, self.frequent_buyer, self.vip_customer]
        self.mock_user_repo.get_users_by_segments_and_location.return_value = (
            expected_users
        )

        # Act
        result = self.service.get_users_by_segments(segments, self.location)

        # Assert
        assert result == expected_users
        self.mock_user_repo.get_users_by_segments_and_location.assert_called_once_with(
            segments, self.location, 2.0
        )

    def test_get_segment_statistics_mixed_users(self):
        """Test getting segment statistics with mixed user types."""
        # Arrange
        # Create a user that is both new and frequent buyer (edge case)
        mixed_user = User(
            id=uuid4(),
            email="mixed@example.com",
            name="Mixed User",
            location=self.location,
            created_at=datetime.now() - timedelta(days=1),  # New user
            total_purchases=20,  # Frequent buyer
            total_spent=800.0,
            last_purchase_at=datetime.now() - timedelta(days=5),  # Recent purchase
        )
        users = [self.new_user, mixed_user, self.vip_customer]

        # Act
        result = self.service.get_segment_statistics(users)

        # Assert
        assert result["total_users"] == 3
        assert result["new_users"] == 2  # new_user and mixed_user
        assert result["frequent_buyers"] == 2  # mixed_user and vip_customer
        assert result["vip_customers"] == 1  # vip_customer
        assert result["users_with_location"] == 3
