"""Tests for reservation views."""
# Standard Python Libraries
from datetime import datetime, timedelta
import json
from unittest.mock import Mock, patch
from uuid import uuid4

# Third-Party Libraries
from django.test import RequestFactory
import pytest
from rest_framework import status
from rest_framework.test import APIClient, force_authenticate

# Local Libraries
from src.presentation.views.reservation_views import (
    check_product_availability,
    get_reservation_status,
    process_purchase,
    reserve_product,
)


class TestReservationViews:
    """Test cases for reservation views."""

    def setup_method(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.client = APIClient()
        self.product_id = uuid4()
        self.user_id = uuid4()
        self.flash_promo_id = uuid4()
        self.reservation_id = uuid4()

    def test_reserve_product_success(self):
        """Test successful product reservation."""
        # Arrange
        request_data = {
            "product_id": str(self.product_id),
            "user_id": str(self.user_id),
            "flash_promo_id": str(self.flash_promo_id),
            "reservation_duration_minutes": 30,
        }
        request = self.factory.post(
            "/reserve/", json.dumps(request_data), content_type="application/json"
        )

        mock_reservation = Mock()
        mock_reservation.id = self.reservation_id
        mock_reservation.product_id = self.product_id
        mock_reservation.user_id = self.user_id
        mock_reservation.flash_promo_id = self.flash_promo_id
        mock_reservation.created_at = datetime.now()
        mock_reservation.expires_at = datetime.now() + timedelta(minutes=30)
        mock_reservation.time_remaining_seconds.return_value = 1800

        with patch(
            "src.infrastructure.container.container.get_reserve_product_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.execute.return_value = mock_reservation
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = reserve_product(request)

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["id"] == str(self.reservation_id)
            assert response.data["product_id"] == str(self.product_id)
            assert response.data["user_id"] == str(self.user_id)
            assert response.data["flash_promo_id"] == str(self.flash_promo_id)
            assert "created_at" in response.data
            assert "expires_at" in response.data
            assert response.data["time_remaining_seconds"] == 1800

    def test_reserve_product_invalid_data(self):
        """Test reservation with invalid data."""
        # Arrange
        request_data = {
            "product_id": "invalid-uuid",
            "user_id": str(self.user_id),
            "flash_promo_id": str(self.flash_promo_id),
            "reservation_duration_minutes": 30,
        }

        request = self.factory.post(
            "/reserve/", json.dumps(request_data), content_type="application/json"
        )

        # Act
        response = reserve_product(request)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "product_id" in response.data

    def test_reserve_product_missing_fields(self):
        """Test reservation with missing required fields."""
        # Arrange
        request_data = {
            "product_id": str(self.product_id),
            "user_id": str(self.user_id),
            # Missing flash_promo_id and reservation_duration_minutes
        }
        request = self.factory.post(
            "/reserve/", json.dumps(request_data), content_type="application/json"
        )

        # Act
        response = reserve_product(request)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "flash_promo_id" in response.data

    def test_reserve_product_already_reserved(self):
        """Test reservation when product is already reserved."""
        # Arrange
        request_data = {
            "product_id": str(self.product_id),
            "user_id": str(self.user_id),
            "flash_promo_id": str(self.flash_promo_id),
            "reservation_duration_minutes": 30,
        }
        request = self.factory.post(
            "/reserve/", json.dumps(request_data), content_type="application/json"
        )

        with patch(
            "src.infrastructure.container.container.get_reserve_product_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.execute.return_value = (
                None  # Product already reserved
            )
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = reserve_product(request)

            # Assert
            assert response.status_code == status.HTTP_409_CONFLICT
            assert "error" in response.data
            assert "already reserved" in response.data["error"]

    def test_reserve_product_value_error(self):
        """Test reservation with ValueError."""
        # Arrange
        request_data = {
            "product_id": str(self.product_id),
            "user_id": str(self.user_id),
            "flash_promo_id": str(self.flash_promo_id),
            "reservation_duration_minutes": 30,
        }
        request = self.factory.post(
            "/reserve/", json.dumps(request_data), content_type="application/json"
        )

        with patch(
            "src.infrastructure.container.container.get_reserve_product_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.execute.side_effect = ValueError("Invalid input")
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = reserve_product(request)

            # Assert
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.data["error"] == "Invalid input"

    def test_reserve_product_general_exception(self):
        """Test reservation with general exception."""
        # Arrange
        request_data = {
            "product_id": str(self.product_id),
            "user_id": str(self.user_id),
            "flash_promo_id": str(self.flash_promo_id),
            "reservation_duration_minutes": 30,
        }
        request = self.factory.post(
            "/reserve/", json.dumps(request_data), content_type="application/json"
        )

        with patch(
            "src.infrastructure.container.container.get_reserve_product_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.execute.side_effect = Exception("Database error")
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = reserve_product(request)

            # Assert
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.data["error"] == "Database error"

    def test_get_reservation_status_success(self):
        """Test successful reservation status retrieval."""
        # Arrange
        request = self.factory.get(f"/reservation/{self.reservation_id}/status/")

        mock_reservation = Mock()
        mock_reservation.id = self.reservation_id
        mock_reservation.is_expired.return_value = False
        mock_reservation.time_remaining_seconds.return_value = 1800
        mock_reservation.expires_at = datetime.now() + timedelta(minutes=30)

        with patch(
            "src.infrastructure.container.container.get_reserve_product_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.get_reservation.return_value = mock_reservation
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = get_reservation_status(request, str(self.reservation_id))

            # Assert
            assert response.status_code == status.HTTP_200_OK
            assert response.data["id"] == str(self.reservation_id)
            assert response.data["is_expired"] is False
            assert response.data["time_remaining_seconds"] == 1800
            assert "expires_at" in response.data

    def test_get_reservation_status_not_found(self):
        """Test reservation status when reservation not found."""
        # Arrange
        request = self.factory.get(f"/reservation/{self.reservation_id}/status/")

        with patch(
            "src.infrastructure.container.container.get_reserve_product_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.get_reservation.return_value = None
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = get_reservation_status(request, str(self.reservation_id))

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "error" in response.data
            assert "not found" in response.data["error"]

    def test_get_reservation_status_invalid_uuid(self):
        """Test reservation status with invalid UUID."""
        # Arrange
        request = self.factory.get("/reservation/invalid-uuid/status/")

        # Act
        response = get_reservation_status(request, "invalid-uuid")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "Invalid reservation ID" in response.data["error"]

    def test_get_reservation_status_general_exception(self):
        """Test reservation status with general exception."""
        # Arrange
        request = self.factory.get(f"/reservation/{self.reservation_id}/status/")

        with patch(
            "src.infrastructure.container.container.get_reserve_product_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.get_reservation.side_effect = Exception(
                "Database error"
            )
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = get_reservation_status(request, str(self.reservation_id))

            # Assert
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.data["error"] == "Database error"

    def test_process_purchase_success(self):
        """Test successful purchase processing."""
        # Arrange
        request_data = {
            "reservation_id": str(self.reservation_id),
            "user_id": str(self.user_id),
        }
        request = self.factory.post(
            "/purchase/", json.dumps(request_data), content_type="application/json"
        )

        mock_price = Mock()
        mock_price.amount = 50.0

        with patch(
            "src.infrastructure.container.container.get_process_purchase_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.execute.return_value = True
            mock_use_case_instance.get_purchase_price.return_value = mock_price
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = process_purchase(request)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            assert response.data["success"] is True
            assert response.data["message"] == "Purchase completed successfully"
            assert response.data["purchase_price"] == 50.0

    def test_process_purchase_invalid_data(self):
        """Test purchase processing with invalid data."""
        # Arrange
        request_data = {
            "reservation_id": "invalid-uuid",
            "user_id": str(self.user_id),
        }
        request = self.factory.post(
            "/purchase/", json.dumps(request_data), content_type="application/json"
        )

        # Act
        response = process_purchase(request)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "reservation_id" in response.data

    def test_process_purchase_missing_fields(self):
        """Test purchase processing with missing fields."""
        # Arrange
        request_data = {
            "reservation_id": str(self.reservation_id),
            # Missing user_id
        }
        request = self.factory.post(
            "/purchase/", json.dumps(request_data), content_type="application/json"
        )

        # Act
        response = process_purchase(request)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "user_id" in response.data

    def test_process_purchase_failed(self):
        """Test purchase processing when purchase fails."""
        # Arrange
        request_data = {
            "reservation_id": str(self.reservation_id),
            "user_id": str(self.user_id),
        }
        request = self.factory.post(
            "/purchase/", json.dumps(request_data), content_type="application/json"
        )

        with patch(
            "src.infrastructure.container.container.get_process_purchase_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.execute.return_value = False  # Purchase failed
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = process_purchase(request)

            # Assert
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "error" in response.data
            assert "could not be processed" in response.data["error"]

    def test_process_purchase_value_error(self):
        """Test purchase processing with ValueError."""
        # Arrange
        request_data = {
            "reservation_id": str(self.reservation_id),
            "user_id": str(self.user_id),
        }
        request = self.factory.post(
            "/purchase/", json.dumps(request_data), content_type="application/json"
        )

        with patch(
            "src.infrastructure.container.container.get_process_purchase_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.execute.side_effect = ValueError("Invalid input")
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = process_purchase(request)

            # Assert
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.data["error"] == "Invalid input"

    def test_process_purchase_general_exception(self):
        """Test purchase processing with general exception."""
        # Arrange
        request_data = {
            "reservation_id": str(self.reservation_id),
            "user_id": str(self.user_id),
        }
        request = self.factory.post(
            "/purchase/", json.dumps(request_data), content_type="application/json"
        )

        with patch(
            "src.infrastructure.container.container.get_process_purchase_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.execute.side_effect = Exception("Database error")
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = process_purchase(request)

            # Assert
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.data["error"] == "Database error"

    def test_check_product_availability_available(self):
        """Test product availability check when product is available."""
        # Arrange
        request = self.factory.get(f"/product/{self.product_id}/availability/")

        with patch(
            "src.infrastructure.container.container.get_reserve_product_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.is_product_reserved.return_value = (
                False  # Not reserved
            )
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = check_product_availability(request, str(self.product_id))

            # Assert
            assert response.status_code == status.HTTP_200_OK
            assert response.data["product_id"] == str(self.product_id)
            assert response.data["is_available"] is True
            assert response.data["is_reserved"] is False

    def test_check_product_availability_reserved(self):
        """Test product availability check when product is reserved."""
        # Arrange
        request = self.factory.get(f"/product/{self.product_id}/availability/")

        with patch(
            "src.infrastructure.container.container.get_reserve_product_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.is_product_reserved.return_value = True  # Reserved
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = check_product_availability(request, str(self.product_id))

            # Assert
            assert response.status_code == status.HTTP_200_OK
            assert response.data["product_id"] == str(self.product_id)
            assert response.data["is_available"] is False
            assert response.data["is_reserved"] is True

    def test_check_product_availability_invalid_uuid(self):
        """Test product availability check with invalid UUID."""
        # Arrange
        request = self.factory.get("/product/invalid-uuid/availability/")

        # Act
        response = check_product_availability(request, "invalid-uuid")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "Invalid product ID" in response.data["error"]

    def test_check_product_availability_general_exception(self):
        """Test product availability check with general exception."""
        # Arrange
        request = self.factory.get(f"/product/{self.product_id}/availability/")

        with patch(
            "src.infrastructure.container.container.get_reserve_product_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.is_product_reserved.side_effect = Exception(
                "Database error"
            )
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = check_product_availability(request, str(self.product_id))

            # Assert
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.data["error"] == "Database error"

    def test_check_product_availability_with_uuid_object(self):
        """Test product availability check when product_id is already a UUID object."""
        # Arrange
        request = self.factory.get(f"/product/{self.product_id}/availability/")

        with patch(
            "src.infrastructure.container.container.get_reserve_product_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.is_product_reserved.return_value = False
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            response = check_product_availability(
                request, self.product_id
            )  # Pass UUID object directly

            # Assert
            assert response.status_code == status.HTTP_200_OK
            assert response.data["product_id"] == str(self.product_id)
            assert response.data["is_available"] is True
            assert response.data["is_reserved"] is False

    def test_process_purchase_with_none_price(self):
        """Test purchase processing when purchase price is None."""
        # Arrange
        request_data = {
            "reservation_id": str(self.reservation_id),
            "user_id": str(self.user_id),
        }
        with patch(
            "src.infrastructure.container.container.get_process_purchase_use_case"
        ) as mock_get_use_case:
            mock_use_case_instance = Mock()
            mock_use_case_instance.execute.return_value = True
            mock_use_case_instance.get_purchase_price.return_value = None  # No price
            mock_get_use_case.return_value = mock_use_case_instance

            # Act
            request = self.factory.post(
                "/purchase/", json.dumps(request_data), content_type="application/json"
            )
            response = process_purchase(request)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            assert response.data["success"] is True
            assert response.data["message"] == "Purchase completed successfully"
            assert response.data["purchase_price"] is None
