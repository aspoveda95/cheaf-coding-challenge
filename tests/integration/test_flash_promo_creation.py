"""Integration tests for Flash Promo creation."""
# Standard Python Libraries
from datetime import time
from decimal import Decimal
from uuid import uuid4

# Third-Party Libraries
from django.test import TestCase
import pytest
from rest_framework.test import APIClient

# Local Libraries
from models.models import FlashPromoModel


class TestFlashPromoCreationIntegration(TestCase):
    """Integration tests for Flash Promo creation."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.product_id = str(uuid4())
        self.store_id = str(uuid4())

    def test_create_flash_promo_saves_to_database(self):
        """Test that creating a flash promo saves it to the database."""
        # Arrange
        data = {
            "product_id": self.product_id,
            "store_id": self.store_id,
            "promo_price": {"amount": "499.00", "currency": "USD"},
            "time_range": {"start_time": "17:00:00", "end_time": "19:00:00"},
            "user_segments": ["new_users", "frequent_buyers"],
            "max_radius_km": 2.0,
        }

        # Act
        response = self.client.post("/api/flash-promos/", data, format="json")

        # Assert
        self.assertEqual(response.status_code, 201)

        # Check response data
        response_data = response.json()
        self.assertIn("id", response_data)
        self.assertEqual(response_data["product_id"], self.product_id)
        self.assertEqual(response_data["store_id"], self.store_id)
        self.assertEqual(response_data["promo_price"]["amount"], "499.00")
        self.assertEqual(
            response_data["is_active"], False
        )  # Should be inactive by default

        # Check database
        promo_id = response_data["id"]
        promo_in_db = FlashPromoModel.objects.get(id=promo_id)
        self.assertEqual(str(promo_in_db.product_id), self.product_id)
        self.assertEqual(str(promo_in_db.store_id), self.store_id)
        self.assertEqual(promo_in_db.promo_price_amount, Decimal("499.00"))
        self.assertEqual(promo_in_db.is_active, False)
        self.assertEqual(
            set(promo_in_db.user_segments), {"new_users", "frequent_buyers"}
        )
        self.assertEqual(promo_in_db.max_radius_km, 2.0)

    def test_create_multiple_flash_promos(self):
        """Test creating multiple flash promos."""
        # Arrange
        base_data = {
            "promo_price": {"amount": "499.00", "currency": "USD"},
            "time_range": {"start_time": "17:00:00", "end_time": "19:00:00"},
            "user_segments": ["new_users"],
            "max_radius_km": 2.0,
        }

        created_promos = []

        # Act - Create 3 promos
        for i in range(3):
            data = {
                **base_data,
                "product_id": str(uuid4()),
                "store_id": str(uuid4()),
            }

            response = self.client.post("/api/flash-promos/", data, format="json")
            self.assertEqual(response.status_code, 201)

            response_data = response.json()
            created_promos.append(response_data["id"])

        # Assert
        self.assertEqual(len(created_promos), 3)

        # Check database has all promos
        db_promos = FlashPromoModel.objects.all()
        self.assertEqual(db_promos.count(), 3)

        # Verify all promos are inactive by default
        for promo in db_promos:
            self.assertFalse(promo.is_active)

    def test_create_flash_promo_with_invalid_data(self):
        """Test creating flash promo with invalid data."""
        # Arrange
        invalid_data = {
            "product_id": "invalid-uuid",
            "store_id": self.store_id,
            "promo_price": {"amount": "499.00", "currency": "USD"},
            "time_range": {"start_time": "17:00:00", "end_time": "19:00:00"},
            "user_segments": ["invalid_segment"],
            "max_radius_km": -1.0,
        }

        # Act
        response = self.client.post("/api/flash-promos/", invalid_data, format="json")

        # Assert
        self.assertEqual(response.status_code, 400)

        # Check no promo was created in database
        db_promos = FlashPromoModel.objects.all()
        self.assertEqual(db_promos.count(), 0)

    def test_create_flash_promo_missing_required_fields(self):
        """Test creating flash promo with missing required fields."""
        # Arrange
        incomplete_data = {
            "product_id": self.product_id,
            # Missing store_id, promo_price, time_range, user_segments
        }

        # Act
        response = self.client.post(
            "/api/flash-promos/", incomplete_data, format="json"
        )

        # Assert
        self.assertEqual(response.status_code, 400)

        # Check no promo was created in database
        db_promos = FlashPromoModel.objects.all()
        self.assertEqual(db_promos.count(), 0)
