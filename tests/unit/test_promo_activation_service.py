"""Tests for PromoActivationService."""
# Standard Python Libraries
from datetime import datetime, time
from unittest.mock import Mock, patch
from uuid import uuid4

# Third-Party Libraries
import pytest

# Local Libraries
from src.application.services.promo_activation_service import PromoActivationService
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.user import User
from src.domain.value_objects.location import Location
from src.domain.value_objects.price import Price
from src.domain.value_objects.time_range import TimeRange
from src.domain.value_objects.user_segment import UserSegment


class TestPromoActivationService:
    """Test cases for PromoActivationService."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock dependencies
        self.mock_flash_promo_repo = Mock()
        self.mock_user_repo = Mock()
        self.mock_email_service = Mock()
        self.mock_push_service = Mock()
        self.mock_sms_service = Mock()
        self.mock_user_segmentation_service = Mock()
        self.mock_notification_service = Mock()

        # Create service instance
        self.service = PromoActivationService(
            flash_promo_repository=self.mock_flash_promo_repo,
            user_repository=self.mock_user_repo,
            email_service=self.mock_email_service,
            push_notification_service=self.mock_push_service,
            sms_service=self.mock_sms_service,
            user_segmentation_service=self.mock_user_segmentation_service,
            notification_service=self.mock_notification_service,
        )

        # Create test data
        self.user1 = User(
            id=uuid4(),
            email="user1@example.com",
            name="User 1",
            location=Location(40.7128, -74.0060),
            segments={UserSegment.NEW_USERS},
        )
        self.user2 = User(
            id=uuid4(),
            email="user2@example.com",
            name="User 2",
            location=Location(40.7589, -73.9851),
            segments={UserSegment.FREQUENT_BUYERS},
        )

        self.promo = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(50.0),
            time_range=TimeRange(time(9, 0, 0), time(18, 0, 0)),
            user_segments=[UserSegment.NEW_USERS, UserSegment.FREQUENT_BUYERS],
            max_radius_km=10.0,
            is_active=True,  # Explicitly set as active for tests
        )

    def test_activate_promos_for_time_with_current_time(self):
        """Test activating promos for a specific time."""
        # Arrange
        current_time = datetime(2023, 1, 1, 12, 0, 0)
        self.mock_flash_promo_repo.get_active_promos.return_value = [self.promo]
        self.mock_user_repo.get_users_by_segments.return_value = [
            self.user1,
            self.user2,
        ]
        self.mock_email_service.send_bulk_flash_promo_email.return_value = {
            "successful_sends": 2,
            "failed_sends": 0,
        }
        self.mock_push_service.send_bulk_flash_promo_push.return_value = {
            "successful_sends": 2,
            "failed_sends": 0,
        }
        self.mock_sms_service.send_bulk_flash_promo_sms.return_value = {
            "successful_sends": 2,
            "failed_sends": 0,
        }

        # Act
        result = self.service.activate_promos_for_time(current_time)

        # Assert
        assert result["activated_promos"] == 1
        assert result["total_notifications_sent"] == 6  # 2 users * 3 channels
        assert len(result["promo_details"]) == 1
        assert result["promo_details"][0]["status"] == "activated"

    def test_activate_promos_for_time_without_current_time(self):
        """Test activating promos without specifying time (uses now)."""
        # Arrange
        with patch(
            "src.application.services.promo_activation_service.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            self.mock_flash_promo_repo.get_active_promos.return_value = [self.promo]
            self.mock_user_repo.get_users_by_segments.return_value = [self.user1]
            self.mock_email_service.send_bulk_flash_promo_email.return_value = {
                "successful_sends": 1,
                "failed_sends": 0,
            }
            self.mock_push_service.send_bulk_flash_promo_push.return_value = {
                "successful_sends": 1,
                "failed_sends": 0,
            }
            self.mock_sms_service.send_bulk_flash_promo_sms.return_value = {
                "successful_sends": 1,
                "failed_sends": 0,
            }

            # Act
            result = self.service.activate_promos_for_time()

            # Assert
            assert result["activated_promos"] == 1
            assert result["total_notifications_sent"] == 3
            mock_datetime.now.assert_called_once()

    def test_activate_promos_for_time_no_active_promos(self):
        """Test activating promos when no promos are active."""
        # Arrange
        current_time = datetime(2023, 1, 1, 12, 0, 0)
        self.mock_flash_promo_repo.get_active_promos.return_value = []

        # Act
        result = self.service.activate_promos_for_time(current_time)

        # Assert
        assert result["activated_promos"] == 0
        assert result["total_notifications_sent"] == 0
        assert result["promo_details"] == []

    def test_get_active_promos(self):
        """Test getting active promos for a specific time."""
        # Arrange
        current_time = datetime(2023, 1, 1, 12, 0, 0)
        self.mock_flash_promo_repo.get_active_promos.return_value = [self.promo]

        # Act
        result = self.service._get_active_promos(current_time)

        # Assert
        assert len(result) == 1
        assert result[0] == self.promo
        self.mock_flash_promo_repo.get_active_promos.assert_called_once()

    def test_activate_single_promo_success(self):
        """Test activating a single promo successfully."""
        # Arrange
        current_time = datetime(2023, 1, 1, 12, 0, 0)
        self.mock_user_repo.get_users_by_segments.return_value = [
            self.user1,
            self.user2,
        ]
        self.mock_email_service.send_bulk_flash_promo_email.return_value = {
            "successful_sends": 2,
            "failed_sends": 0,
        }
        self.mock_push_service.send_bulk_flash_promo_push.return_value = {
            "successful_sends": 2,
            "failed_sends": 0,
        }
        self.mock_sms_service.send_bulk_flash_promo_sms.return_value = {
            "successful_sends": 2,
            "failed_sends": 0,
        }

        # Act
        result = self.service._activate_single_promo(self.promo, current_time)

        # Assert
        assert result["promo_id"] == str(self.promo.id)
        assert result["eligible_users"] == 2
        assert result["notifications_sent"] == 6  # 2 users * 3 channels
        assert result["status"] == "activated"

    def test_activate_single_promo_no_eligible_users(self):
        """Test activating a single promo with no eligible users."""
        # Arrange
        current_time = datetime(2023, 1, 1, 12, 0, 0)
        self.mock_user_repo.get_users_by_segments.return_value = []

        # Act
        result = self.service._activate_single_promo(self.promo, current_time)

        # Assert
        assert result["promo_id"] == str(self.promo.id)
        assert result["eligible_users"] == 0
        assert result["notifications_sent"] == 0
        assert result["status"] == "no_eligible_users"

    def test_activate_single_promo_with_failures(self):
        """Test activating a single promo with some notification failures."""
        # Arrange
        current_time = datetime(2023, 1, 1, 12, 0, 0)
        self.mock_user_repo.get_users_by_segments.return_value = [
            self.user1,
            self.user2,
        ]
        self.mock_email_service.send_bulk_flash_promo_email.return_value = {
            "successful_sends": 1,
            "failed_sends": 1,
        }
        self.mock_push_service.send_bulk_flash_promo_push.return_value = {
            "successful_sends": 2,
            "failed_sends": 0,
        }
        self.mock_sms_service.send_bulk_flash_promo_sms.return_value = {
            "successful_sends": 1,
            "failed_sends": 1,
        }

        # Act
        result = self.service._activate_single_promo(self.promo, current_time)

        # Assert
        assert result["promo_id"] == str(self.promo.id)
        assert result["eligible_users"] == 2
        assert result["notifications_sent"] == 4  # 1+2+1 successful
        assert result["status"] == "activated"

    def test_get_eligible_users_for_promo_with_segments(self):
        """Test getting eligible users for a promo with segments."""
        # Arrange
        self.mock_user_repo.get_users_by_segments.return_value = [
            self.user1,
            self.user2,
        ]

        # Act
        result = self.service._get_eligible_users_for_promo(self.promo)

        # Assert
        assert len(result) == 2
        assert result == [self.user1, self.user2]
        self.mock_user_repo.get_users_by_segments.assert_called_once_with(
            self.promo.user_segments
        )

    def test_get_eligible_users_for_promo_no_segments(self):
        """Test getting eligible users for a promo without segments."""
        # Arrange
        promo_no_segments = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(50.0),
            time_range=TimeRange(time(9, 0, 0), time(18, 0, 0)),
            user_segments=[],
            max_radius_km=10.0,
            is_active=True,  # Explicitly set as active for tests
        )

        # Act
        result = self.service._get_eligible_users_for_promo(promo_no_segments)

        # Assert
        assert result == []

    def test_get_promo_eligibility_success(self):
        """Test checking promo eligibility for eligible user."""
        # Arrange
        self.mock_flash_promo_repo.get_by_id.return_value = self.promo
        self.mock_user_repo.get_by_id.return_value = self.user1
        with patch.object(self.promo, "is_currently_active", return_value=True):
            with patch.object(self.promo, "is_eligible_for_user", return_value=True):
                # Act
                result = self.service.get_promo_eligibility(
                    self.promo.id, self.user1.id
                )

                # Assert
                assert result["eligible"] is True
                assert result["reason"] == "User is eligible"
                self.mock_flash_promo_repo.get_by_id.assert_called_once_with(
                    self.promo.id
                )
                self.mock_user_repo.get_by_id.assert_called_once_with(self.user1.id)

    def test_get_promo_eligibility_promo_not_found(self):
        """Test checking promo eligibility when promo is not found."""
        # Arrange
        self.mock_flash_promo_repo.get_by_id.return_value = None

        # Act
        result = self.service.get_promo_eligibility(self.promo.id, self.user1.id)

        # Assert
        assert result["eligible"] is False
        assert result["reason"] == "Promo not found"

    def test_get_promo_eligibility_promo_not_active(self):
        """Test checking promo eligibility when promo is not active."""
        # Arrange
        inactive_promo = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(50.0),
            time_range=TimeRange(time(9, 0, 0), time(10, 0, 0)),  # Past time range
            user_segments=[UserSegment.NEW_USERS],
            max_radius_km=10.0,
        )
        self.mock_flash_promo_repo.get_by_id.return_value = inactive_promo

        # Act
        result = self.service.get_promo_eligibility(inactive_promo.id, self.user1.id)

        # Assert
        assert result["eligible"] is False
        assert result["reason"] == "Promo not currently active"

    def test_get_promo_eligibility_user_not_found(self):
        """Test checking promo eligibility when user is not found."""
        # Arrange
        self.mock_flash_promo_repo.get_by_id.return_value = self.promo
        self.mock_user_repo.get_by_id.return_value = None
        with patch.object(self.promo, "is_currently_active", return_value=True):
            # Act
            result = self.service.get_promo_eligibility(self.promo.id, self.user1.id)

            # Assert
            assert result["eligible"] is False
            assert result["reason"] == "User not found"

    def test_get_promo_eligibility_user_segments_not_eligible(self):
        """Test checking promo eligibility when user segments are not eligible."""
        # Arrange
        user_different_segments = User(
            id=uuid4(),
            email="user@example.com",
            name="User",
            location=Location(40.7128, -74.0060),
            segments={UserSegment.VIP_CUSTOMERS},  # Different segment
        )
        self.mock_flash_promo_repo.get_by_id.return_value = self.promo
        self.mock_user_repo.get_by_id.return_value = user_different_segments
        with patch.object(self.promo, "is_currently_active", return_value=True):
            with patch.object(self.promo, "is_eligible_for_user", return_value=False):
                # Act
                result = self.service.get_promo_eligibility(
                    self.promo.id, user_different_segments.id
                )

                # Assert
                assert result["eligible"] is False
                assert result["reason"] == "User segments not eligible"

    def test_schedule_promo_activation_success(self):
        """Test scheduling promo activation successfully."""
        # Arrange
        self.mock_flash_promo_repo.get_by_id.return_value = self.promo

        # Act
        result = self.service.schedule_promo_activation(self.promo.id)

        # Assert
        assert result is True
        self.mock_flash_promo_repo.get_by_id.assert_called_once_with(self.promo.id)

    def test_schedule_promo_activation_promo_not_found(self):
        """Test scheduling promo activation when promo is not found."""
        # Arrange
        self.mock_flash_promo_repo.get_by_id.return_value = None

        # Act
        result = self.service.schedule_promo_activation(self.promo.id)

        # Assert
        assert result is False

    def test_schedule_promo_activation_no_time_range(self):
        """Test scheduling promo activation when promo has no time range."""
        # Arrange
        promo_no_time = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(50.0),
            time_range=None,
            user_segments=[UserSegment.NEW_USERS],
            max_radius_km=10.0,
            is_active=True,  # Explicitly set as active for tests
        )
        self.mock_flash_promo_repo.get_by_id.return_value = promo_no_time

        # Act
        result = self.service.schedule_promo_activation(promo_no_time.id)

        # Assert
        assert result is False

    def test_get_promo_statistics_success(self):
        """Test getting promo statistics successfully."""
        # Arrange
        self.mock_flash_promo_repo.get_by_id.return_value = self.promo
        self.mock_user_repo.get_users_by_segments.return_value = [
            self.user1,
            self.user2,
        ]
        with patch.object(self.promo, "is_currently_active", return_value=True):
            # Act
            result = self.service.get_promo_statistics(self.promo.id)

            # Assert
            assert result["promo_id"] == str(self.promo.id)
            assert result["is_active"] is True
            assert result["eligible_users_count"] == 2
            assert result["user_segments"] == [
                seg.value for seg in self.promo.user_segments
            ]
            assert result["time_range"] == {
                "start_time": "09:00:00",
                "end_time": "18:00:00",
            }
            assert result["promo_price"] == {
                "amount": "50.0",
                "currency": "USD",
            }

    def test_get_promo_statistics_promo_not_found(self):
        """Test getting promo statistics when promo is not found."""
        # Arrange
        self.mock_flash_promo_repo.get_by_id.return_value = None

        # Act
        result = self.service.get_promo_statistics(self.promo.id)

        # Assert
        assert result["error"] == "Promo not found"

    def test_get_promo_statistics_inactive_promo(self):
        """Test getting promo statistics for inactive promo."""
        # Arrange
        inactive_promo = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(50.0),
            time_range=TimeRange(time(9, 0, 0), time(10, 0, 0)),  # Past time range
            user_segments=[UserSegment.NEW_USERS],
            max_radius_km=10.0,
        )
        self.mock_flash_promo_repo.get_by_id.return_value = inactive_promo
        self.mock_user_repo.get_users_by_segments.return_value = []

        # Act
        result = self.service.get_promo_statistics(inactive_promo.id)

        # Assert
        assert result["promo_id"] == str(inactive_promo.id)
        assert result["is_active"] is False
        assert result["eligible_users_count"] == 0

    def test_get_promo_statistics_promo_without_time_range(self):
        """Test getting promo statistics for promo without time range."""
        # Arrange
        promo_no_time = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(50.0),
            time_range=None,
            user_segments=[UserSegment.NEW_USERS],
            max_radius_km=10.0,
        )
        self.mock_flash_promo_repo.get_by_id.return_value = promo_no_time
        self.mock_user_repo.get_users_by_segments.return_value = [self.user1]

        # Act
        result = self.service.get_promo_statistics(promo_no_time.id)

        # Assert
        assert result["promo_id"] == str(promo_no_time.id)
        assert result["time_range"] is None

    def test_get_promo_statistics_promo_without_price(self):
        """Test getting promo statistics for promo without price."""
        # Arrange
        promo_no_price = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=None,
            time_range=TimeRange(time(9, 0, 0), time(18, 0, 0)),
            user_segments=[UserSegment.NEW_USERS],
            max_radius_km=10.0,
            is_active=True,  # Explicitly set as active for tests
        )
        self.mock_flash_promo_repo.get_by_id.return_value = promo_no_price
        self.mock_user_repo.get_users_by_segments.return_value = [self.user1]

        # Act
        result = self.service.get_promo_statistics(promo_no_price.id)

        # Assert
        assert result["promo_id"] == str(promo_no_price.id)
        assert result["promo_price"] is None

    def test_activate_promos_for_time_multiple_promos(self):
        """Test activating multiple promos."""
        # Arrange
        promo2 = FlashPromo(
            id=uuid4(),
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(75.0),
            time_range=TimeRange(time(14, 0, 0), time(16, 0, 0)),
            user_segments=[UserSegment.VIP_CUSTOMERS],
            max_radius_km=5.0,
            is_active=True,  # Explicitly set as active for tests
        )

        current_time = datetime(
            2023, 1, 1, 15, 0, 0
        )  # 15:00 is within both time ranges
        self.mock_flash_promo_repo.get_active_promos.return_value = [self.promo, promo2]
        self.mock_user_repo.get_users_by_segments.return_value = [
            self.user1,
            self.user2,
        ]
        self.mock_email_service.send_bulk_flash_promo_email.return_value = {
            "successful_sends": 2,
            "failed_sends": 0,
        }
        self.mock_push_service.send_bulk_flash_promo_push.return_value = {
            "successful_sends": 2,
            "failed_sends": 0,
        }
        self.mock_sms_service.send_bulk_flash_promo_sms.return_value = {
            "successful_sends": 2,
            "failed_sends": 0,
        }

        # Act
        result = self.service.activate_promos_for_time(current_time)

        # Assert
        assert result["activated_promos"] == 2
        assert (
            result["total_notifications_sent"] == 12
        )  # 2 promos * 2 users * 3 channels
        assert len(result["promo_details"]) == 2
