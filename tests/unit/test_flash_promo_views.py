"""Tests for flash promo views."""
# Standard Python Libraries
from datetime import datetime, time
from decimal import Decimal
import json
from unittest.mock import Mock, patch
from uuid import uuid4

# Third-Party Libraries
from django.test import RequestFactory
import pytest
from rest_framework import status

# Local Libraries
from src.presentation.views.flash_promo_views import (
    activate_flash_promo,
    check_promo_eligibility,
    create_flash_promo,
    get_active_flash_promos,
    get_promo_statistics,
)


class TestFlashPromoViews:
    """Test cases for flash promo views."""

    def setup_method(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.product_id = uuid4()
        self.store_id = uuid4()
        self.promo_id = uuid4()
        self.user_id = uuid4()

    def test_create_flash_promo_success(self):
        """Test successful flash promo creation."""
        # Arrange
        request_data = {
            "product_id": str(self.product_id),
            "store_id": str(self.store_id),
            "promo_price": {"amount": "50.00"},
            "time_range": {
                "start_time": "09:00:00",
                "end_time": "18:00:00",
            },
            "user_segments": ["new_users", "frequent_buyers"],
            "max_radius_km": 10.0,
        }
        request = self.factory.post(
            "/flash-promos/", json.dumps(request_data), content_type="application/json"
        )

        mock_flash_promo = Mock()
        mock_flash_promo.id = self.promo_id
        mock_flash_promo.product_id = self.product_id
        mock_flash_promo.store_id = self.store_id
        mock_flash_promo.promo_price = Mock()
        mock_flash_promo.promo_price.amount = Decimal("50.00")
        mock_flash_promo.time_range = Mock()
        mock_flash_promo.time_range.start_time = time(9, 0, 0)
        mock_flash_promo.time_range.end_time = time(18, 0, 0)
        mock_flash_promo.user_segments = [
            Mock(value="new_users"),
            Mock(value="frequent_buyers"),
        ]
        mock_flash_promo.max_radius_km = 10.0
        mock_flash_promo.is_active = False
        mock_flash_promo.created_at = datetime.now()

        with patch("src.infrastructure.container.container") as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = mock_flash_promo
            mock_container.get_create_flash_promo_use_case.return_value = mock_use_case

            # Act
            response = create_flash_promo(request)

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["id"] == str(self.promo_id)
            assert response.data["product_id"] == str(self.product_id)
            assert response.data["store_id"] == str(self.store_id)
            assert response.data["promo_price"]["amount"] == "50.00"
            assert response.data["time_range"]["start_time"] == "09:00:00"
            assert response.data["time_range"]["end_time"] == "18:00:00"
            assert response.data["user_segments"] == ["new_users", "frequent_buyers"]
            assert response.data["max_radius_km"] == 10.0
            assert response.data["is_active"] is False

    def test_create_flash_promo_invalid_data(self):
        """Test flash promo creation with invalid data."""
        # Arrange
        request_data = {
            "product_id": "invalid-uuid",
            "store_id": str(self.store_id),
            "promo_price": {"amount": "50.00"},
            "time_range": {
                "start_time": "09:00:00",
                "end_time": "18:00:00",
            },
            "user_segments": ["new_users"],
            "max_radius_km": 10.0,
        }
        request = self.factory.post(
            "/flash-promos/", json.dumps(request_data), content_type="application/json"
        )

        # Act
        response = create_flash_promo(request)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "product_id" in response.data

    def test_create_flash_promo_missing_fields(self):
        """Test flash promo creation with missing required fields."""
        # Arrange
        request_data = {
            "product_id": str(self.product_id),
            "store_id": str(self.store_id),
            # Missing required fields
        }
        request = self.factory.post(
            "/flash-promos/", json.dumps(request_data), content_type="application/json"
        )

        # Act
        response = create_flash_promo(request)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "promo_price" in response.data

    def test_create_flash_promo_with_time_objects(self):
        """Test flash promo creation with time objects instead of strings."""
        # Arrange
        request_data = {
            "product_id": str(self.product_id),
            "store_id": str(self.store_id),
            "promo_price": {"amount": "50.00"},
            "time_range": {
                "start_time": "09:00:00",
                "end_time": "18:00:00",
            },
            "user_segments": ["new_users"],
            "max_radius_km": 10.0,
        }
        request = self.factory.post(
            "/flash-promos/", json.dumps(request_data), content_type="application/json"
        )

        mock_flash_promo = Mock()
        mock_flash_promo.id = self.promo_id
        mock_flash_promo.product_id = self.product_id
        mock_flash_promo.store_id = self.store_id
        mock_flash_promo.promo_price = Mock()
        mock_flash_promo.promo_price.amount = Decimal("50.00")
        mock_flash_promo.time_range = Mock()
        mock_flash_promo.time_range.start_time = time(9, 0, 0)
        mock_flash_promo.time_range.end_time = time(18, 0, 0)
        mock_flash_promo.user_segments = [Mock(value="new_users")]
        mock_flash_promo.max_radius_km = 10.0
        mock_flash_promo.is_active = False
        mock_flash_promo.created_at = datetime.now()

        with patch("src.infrastructure.container.container") as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = mock_flash_promo
            mock_container.get_create_flash_promo_use_case.return_value = mock_use_case

            # Act
            response = create_flash_promo(request)

            # Assert
            assert response.status_code == status.HTTP_201_CREATED

    def test_create_flash_promo_with_uuid_objects(self):
        """Test flash promo creation with UUID objects instead of strings."""
        # Arrange
        request_data = {
            "product_id": str(self.product_id),
            "store_id": str(self.store_id),
            "promo_price": {"amount": "50.00"},
            "time_range": {
                "start_time": "09:00:00",
                "end_time": "18:00:00",
            },
            "user_segments": ["new_users"],
            "max_radius_km": 10.0,
        }
        request = self.factory.post(
            "/flash-promos/", json.dumps(request_data), content_type="application/json"
        )

        mock_flash_promo = Mock()
        mock_flash_promo.id = self.promo_id
        mock_flash_promo.product_id = self.product_id
        mock_flash_promo.store_id = self.store_id
        mock_flash_promo.promo_price = Mock()
        mock_flash_promo.promo_price.amount = Decimal("50.00")
        mock_flash_promo.time_range = Mock()
        mock_flash_promo.time_range.start_time = time(9, 0, 0)
        mock_flash_promo.time_range.end_time = time(18, 0, 0)
        mock_flash_promo.user_segments = [Mock(value="new_users")]
        mock_flash_promo.max_radius_km = 10.0
        mock_flash_promo.is_active = False
        mock_flash_promo.created_at = datetime.now()

        with patch("src.infrastructure.container.container") as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = mock_flash_promo
            mock_container.get_create_flash_promo_use_case.return_value = mock_use_case

            # Act
            response = create_flash_promo(request)

            # Assert
            assert response.status_code == status.HTTP_201_CREATED

    def test_create_flash_promo_exception(self):
        """Test flash promo creation with exception."""
        # Arrange
        request_data = {
            "product_id": str(self.product_id),
            "store_id": str(self.store_id),
            "promo_price": {"amount": "50.00"},
            "time_range": {
                "start_time": "09:00:00",
                "end_time": "18:00:00",
            },
            "user_segments": ["new_users"],
            "max_radius_km": 10.0,
        }
        request = self.factory.post(
            "/flash-promos/", json.dumps(request_data), content_type="application/json"
        )

        with patch("src.infrastructure.container.container") as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.side_effect = Exception("Database error")
            mock_container.get_create_flash_promo_use_case.return_value = mock_use_case

            # Act
            response = create_flash_promo(request)

            # Assert
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "error" in response.data

    def test_get_active_flash_promos_success(self):
        """Test successful retrieval of active flash promos."""
        # Arrange
        request = self.factory.get("/flash-promos/active/")

        mock_promo1 = Mock()
        mock_promo1.id = self.promo_id
        mock_promo1.product_id = self.product_id
        mock_promo1.store_id = self.store_id
        mock_promo1.promo_price = Mock()
        mock_promo1.promo_price.amount = Decimal("50.00")
        mock_promo1.time_range = Mock()
        mock_promo1.time_range.start_time = time(9, 0, 0)
        mock_promo1.time_range.end_time = time(18, 0, 0)
        mock_promo1.user_segments = [Mock(value="new_users")]
        mock_promo1.max_radius_km = 2.0
        mock_promo1.is_active = True
        mock_promo1.created_at = datetime.now()

        mock_promo2 = Mock()
        mock_promo2.id = uuid4()
        mock_promo2.product_id = uuid4()
        mock_promo2.store_id = uuid4()
        mock_promo2.promo_price = Mock()
        mock_promo2.promo_price.amount = Decimal("75.00")
        mock_promo2.time_range = Mock()
        mock_promo2.time_range.start_time = time(14, 0, 0)
        mock_promo2.time_range.end_time = time(16, 0, 0)
        mock_promo2.user_segments = [Mock(value="frequent_buyers")]
        mock_promo2.max_radius_km = 3.0
        mock_promo2.is_active = True
        mock_promo2.created_at = datetime.now()

        with patch(
            "src.presentation.views.flash_promo_views.DjangoFlashPromoRepository"
        ) as mock_flash_repo, patch(
            "src.presentation.views.flash_promo_views.DjangoUserRepository"
        ) as mock_user_repo, patch(
            "src.presentation.views.flash_promo_views.ActivateFlashPromoUseCase"
        ) as mock_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.get_active_promos.return_value = [
                mock_promo1,
                mock_promo2,
            ]
            mock_use_case.return_value = mock_use_case_instance

            # Act
            response = get_active_flash_promos(request)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 2
            assert response.data[0]["id"] == str(self.promo_id)
            assert response.data[1]["id"] == str(mock_promo2.id)

    def test_get_active_flash_promos_empty(self):
        """Test retrieval of active flash promos when none are active."""
        # Arrange
        request = self.factory.get("/flash-promos/active/")

        with patch(
            "src.presentation.views.flash_promo_views.DjangoFlashPromoRepository"
        ) as mock_flash_repo, patch(
            "src.presentation.views.flash_promo_views.DjangoUserRepository"
        ) as mock_user_repo, patch(
            "src.presentation.views.flash_promo_views.ActivateFlashPromoUseCase"
        ) as mock_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.get_active_promos.return_value = []
            mock_use_case.return_value = mock_use_case_instance

            # Act
            response = get_active_flash_promos(request)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == 0

    def test_get_active_flash_promos_exception(self):
        """Test retrieval of active flash promos with exception."""
        # Arrange
        request = self.factory.get("/flash-promos/active/")

        with patch(
            "src.presentation.views.flash_promo_views.DjangoFlashPromoRepository"
        ) as mock_flash_repo, patch(
            "src.presentation.views.flash_promo_views.DjangoUserRepository"
        ) as mock_user_repo, patch(
            "src.presentation.views.flash_promo_views.ActivateFlashPromoUseCase"
        ) as mock_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.get_active_promos.side_effect = Exception(
                "Database error"
            )
            mock_use_case.return_value = mock_use_case_instance

            # Act
            response = get_active_flash_promos(request)

            # Assert
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "error" in response.data

    def test_activate_flash_promo_success(self):
        """Test successful flash promo activation."""
        # Arrange
        request_data = {"promo_id": str(self.promo_id)}
        request = self.factory.post(
            "/flash-promos/activate/",
            json.dumps(request_data),
            content_type="application/json",
        )

        mock_activated_promo = Mock()
        mock_activated_promo.id = self.promo_id

        with patch("src.infrastructure.container.container") as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = mock_activated_promo
            mock_container.get_activate_flash_promo_use_case.return_value = (
                mock_use_case
            )

            # Act
            response = activate_flash_promo(request)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            assert response.data["message"] == "Flash promo activated successfully"
            assert response.data["promo_id"] == str(self.promo_id)

    def test_activate_flash_promo_invalid_data(self):
        """Test flash promo activation with invalid data."""
        # Arrange
        request_data = {"promo_id": "invalid-uuid"}
        request = self.factory.post(
            "/flash-promos/activate/",
            json.dumps(request_data),
            content_type="application/json",
        )

        # Act
        response = activate_flash_promo(request)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "promo_id" in response.data

    def test_activate_flash_promo_missing_fields(self):
        """Test flash promo activation with missing fields."""
        # Arrange
        request_data = {}  # Missing promo_id
        request = self.factory.post(
            "/flash-promos/activate/",
            json.dumps(request_data),
            content_type="application/json",
        )

        # Act
        response = activate_flash_promo(request)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "promo_id" in response.data

    def test_activate_flash_promo_with_uuid_object(self):
        """Test flash promo activation with UUID object."""
        # Arrange
        request_data = {"promo_id": str(self.promo_id)}
        request = self.factory.post(
            "/flash-promos/activate/",
            json.dumps(request_data),
            content_type="application/json",
        )

        mock_activated_promo = Mock()
        mock_activated_promo.id = self.promo_id

        with patch("src.infrastructure.container.container") as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.return_value = mock_activated_promo
            mock_container.get_activate_flash_promo_use_case.return_value = (
                mock_use_case
            )

            # Act
            response = activate_flash_promo(request)

            # Assert
            assert response.status_code == status.HTTP_200_OK

    def test_activate_flash_promo_value_error(self):
        """Test flash promo activation with ValueError."""
        # Arrange
        request_data = {"promo_id": str(self.promo_id)}
        request = self.factory.post(
            "/flash-promos/activate/",
            json.dumps(request_data),
            content_type="application/json",
        )

        with patch("src.infrastructure.container.container") as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.side_effect = ValueError("Promo not found")
            mock_container.get_activate_flash_promo_use_case.return_value = (
                mock_use_case
            )

            # Act
            response = activate_flash_promo(request)

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "error" in response.data

    def test_activate_flash_promo_exception(self):
        """Test flash promo activation with general exception."""
        # Arrange
        request_data = {"promo_id": str(self.promo_id)}
        request = self.factory.post(
            "/flash-promos/activate/",
            json.dumps(request_data),
            content_type="application/json",
        )

        with patch("src.infrastructure.container.container") as mock_container:
            mock_use_case = Mock()
            mock_use_case.execute.side_effect = Exception("Database error")
            mock_container.get_activate_flash_promo_use_case.return_value = (
                mock_use_case
            )

            # Act
            response = activate_flash_promo(request)

            # Assert
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "error" in response.data

    def test_check_promo_eligibility_success(self):
        """Test successful promo eligibility check."""
        # Arrange
        request_data = {
            "promo_id": str(self.promo_id),
            "user_id": str(self.user_id),
        }
        request = self.factory.post(
            "/flash-promos/eligibility/",
            json.dumps(request_data),
            content_type="application/json",
        )

        mock_eligibility_result = {
            "eligible": True,
            "reason": "User is eligible",
            "promo_id": str(self.promo_id),
            "user_id": str(self.user_id),
        }

        with patch("src.infrastructure.container.container") as mock_container:
            mock_service = Mock()
            mock_service.get_promo_eligibility.return_value = mock_eligibility_result
            mock_container.get_promo_activation_service.return_value = mock_service

            # Act
            response = check_promo_eligibility(request)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            assert response.data["eligible"] is True
            assert response.data["reason"] == "User is eligible"

    def test_check_promo_eligibility_invalid_data(self):
        """Test promo eligibility check with invalid data."""
        # Arrange
        request_data = {
            "promo_id": "invalid-uuid",
            "user_id": str(self.user_id),
        }
        request = self.factory.post(
            "/flash-promos/eligibility/",
            json.dumps(request_data),
            content_type="application/json",
        )

        # Act
        response = check_promo_eligibility(request)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "promo_id" in response.data

    def test_check_promo_eligibility_missing_fields(self):
        """Test promo eligibility check with missing fields."""
        # Arrange
        request_data = {"promo_id": str(self.promo_id)}  # Missing user_id
        request = self.factory.post(
            "/flash-promos/eligibility/",
            json.dumps(request_data),
            content_type="application/json",
        )

        # Act
        response = check_promo_eligibility(request)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "user_id" in response.data

    def test_check_promo_eligibility_with_uuid_objects(self):
        """Test promo eligibility check with UUID objects."""
        # Arrange
        request_data = {
            "promo_id": str(self.promo_id),
            "user_id": str(self.user_id),
        }
        request = self.factory.post(
            "/flash-promos/eligibility/",
            json.dumps(request_data),
            content_type="application/json",
        )

        mock_eligibility_result = {
            "eligible": True,
            "reason": "User is eligible",
        }

        with patch("src.infrastructure.container.container") as mock_container:
            mock_service = Mock()
            mock_service.get_promo_eligibility.return_value = mock_eligibility_result
            mock_container.get_promo_activation_service.return_value = mock_service

            # Act
            response = check_promo_eligibility(request)

            # Assert
            assert response.status_code == status.HTTP_200_OK

    def test_check_promo_eligibility_exception(self):
        """Test promo eligibility check with exception."""
        # Arrange
        request_data = {
            "promo_id": str(self.promo_id),
            "user_id": str(self.user_id),
        }
        request = self.factory.post(
            "/flash-promos/eligibility/",
            json.dumps(request_data),
            content_type="application/json",
        )

        with patch("src.infrastructure.container.container") as mock_container:
            mock_service = Mock()
            mock_service.get_promo_eligibility.side_effect = Exception("Database error")
            mock_container.get_promo_activation_service.return_value = mock_service

            # Act
            response = check_promo_eligibility(request)

            # Assert
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "error" in response.data

    def test_get_promo_statistics_success(self):
        """Test successful promo statistics retrieval."""
        # Arrange
        request = self.factory.get(f"/flash-promos/{self.promo_id}/statistics/")

        mock_stats = {
            "promo_id": str(self.promo_id),
            "is_active": True,
            "eligible_users_count": 100,
            "user_segments": ["new_users", "frequent_buyers"],
            "time_range": "09:00:00 - 18:00:00",
            "promo_price": "50.00",
        }

        with patch(
            "src.infrastructure.container.container.get_promo_activation_service"
        ) as mock_get_service:
            mock_service_instance = Mock()
            mock_service_instance.get_promo_statistics.return_value = mock_stats
            mock_get_service.return_value = mock_service_instance

            # Act
            response = get_promo_statistics(request, str(self.promo_id))

            # Assert
            assert response.status_code == status.HTTP_200_OK
            assert response.data["promo_id"] == str(self.promo_id)
            assert response.data["is_active"] is True
            assert response.data["eligible_users_count"] == 100

    def test_get_promo_statistics_invalid_uuid(self):
        """Test promo statistics retrieval with invalid UUID."""
        # Arrange
        request = self.factory.get("/flash-promos/invalid-uuid/statistics/")

        # Act
        response = get_promo_statistics(request, "invalid-uuid")

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error" in response.data

    def test_get_promo_statistics_exception(self):
        """Test promo statistics retrieval with exception."""
        # Arrange
        request = self.factory.get(f"/flash-promos/{self.promo_id}/statistics/")

        with patch(
            "src.infrastructure.container.container.get_promo_activation_service"
        ) as mock_get_service:
            mock_service_instance = Mock()
            mock_service_instance.get_promo_statistics.side_effect = Exception(
                "Database error"
            )
            mock_get_service.return_value = mock_service_instance

            # Act
            response = get_promo_statistics(request, str(self.promo_id))

            # Assert
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "error" in response.data
