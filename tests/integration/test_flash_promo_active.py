"""Integration tests for Flash Promo active endpoints."""
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
from src.domain.entities.flash_promo import FlashPromo
from src.domain.value_objects.price import Price
from src.domain.value_objects.time_range import TimeRange
from src.domain.value_objects.user_segment import UserSegment
from src.infrastructure.repositories.django_flash_promo_repository import (
    DjangoFlashPromoRepository,
)


class TestFlashPromoActiveIntegration(TestCase):
    """Integration tests for Flash Promo active endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.product_id = str(uuid4())
        self.store_id = str(uuid4())
        self.repo = DjangoFlashPromoRepository()

    def test_get_active_promos_empty_when_no_promos(self):
        """Test getting active promos when no promos exist."""
        # Act
        response = self.client.get("/api/flash-promos/active/")

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data, [])

    def test_get_active_promos_empty_when_all_inactive(self):
        """Test getting active promos when all promos are inactive."""
        # Arrange - Create inactive promo
        promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(Decimal("499.00")),
            time_range=TimeRange(time(17, 0), time(19, 0)),
            user_segments={UserSegment.NEW_USERS},
            max_radius_km=2.0,
            is_active=False,  # Inactive
        )
        self.repo.save(promo)

        # Act
        response = self.client.get("/api/flash-promos/active/")

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data, [])

    def test_get_active_promos_returns_active_promos(self):
        """Test getting active promos returns only active ones."""
        # Arrange - Create inactive promo
        inactive_promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(Decimal("499.00")),
            time_range=TimeRange(time(17, 0), time(19, 0)),
            user_segments={UserSegment.NEW_USERS},
            max_radius_km=2.0,
            is_active=False,  # Inactive
        )
        self.repo.save(inactive_promo)

        # Arrange - Create active promo
        active_promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(Decimal("299.00")),
            time_range=TimeRange(time(17, 0), time(19, 0)),
            user_segments={UserSegment.FREQUENT_BUYERS},
            max_radius_km=5.0,
            is_active=True,  # Active
        )
        self.repo.save(active_promo)

        # Act
        response = self.client.get("/api/flash-promos/active/")

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data), 1)

        # Check active promo data
        active_promo_data = response_data[0]
        self.assertEqual(active_promo_data["product_id"], str(active_promo.product_id))
        self.assertEqual(active_promo_data["store_id"], str(active_promo.store_id))
        self.assertEqual(active_promo_data["promo_price"]["amount"], "299.00")
        self.assertEqual(active_promo_data["is_active"], True)
        self.assertEqual(set(active_promo_data["user_segments"]), {"frequent_buyers"})
        self.assertEqual(active_promo_data["max_radius_km"], "5.00")

    def test_get_active_promos_multiple_active(self):
        """Test getting multiple active promos."""
        # Arrange - Create multiple active promos
        active_promos = []
        for i in range(3):
            promo = FlashPromo(
                product_id=uuid4(),
                store_id=uuid4(),
                promo_price=Price(Decimal(f"{100 + i * 50}.00")),
                time_range=TimeRange(time(17, 0), time(19, 0)),
                user_segments={UserSegment.NEW_USERS},
                max_radius_km=2.0,
                is_active=True,  # Active
            )
            saved_promo = self.repo.save(promo)
            active_promos.append(saved_promo)

        # Act
        response = self.client.get("/api/flash-promos/active/")

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data), 3)

        # Check all promos are active
        for promo_data in response_data:
            self.assertTrue(promo_data["is_active"])

    def test_get_active_promos_returns_all_active_promos(self):
        """Test that active promos endpoint returns all active promos regardless of time."""
        # Arrange - Create promo with past time range
        past_promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(Decimal("499.00")),
            time_range=TimeRange(time(9, 0), time(11, 0)),  # Past time range
            user_segments={UserSegment.NEW_USERS},
            max_radius_km=2.0,
            is_active=True,  # Active but outside time range
        )
        self.repo.save(past_promo)

        # Arrange - Create promo with current time range
        current_promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(Decimal("299.00")),
            time_range=TimeRange(time(17, 0), time(19, 0)),  # Current time range
            user_segments={UserSegment.FREQUENT_BUYERS},
            max_radius_km=5.0,
            is_active=True,  # Active and in time range
        )
        self.repo.save(current_promo)

        # Act
        response = self.client.get("/api/flash-promos/active/")

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        # Should return all active promos regardless of time range
        # This is correct for a global API
        self.assertEqual(len(response_data), 2)

        # Check that both promos are returned
        promo_ids = [promo["id"] for promo in response_data]
        self.assertIn(str(past_promo.id), promo_ids)
        self.assertIn(str(current_promo.id), promo_ids)

    def test_get_active_promos_response_format(self):
        """Test that active promos response has correct format."""
        # Arrange - Create active promo
        promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(Decimal("199.00")),
            time_range=TimeRange(time(17, 0), time(19, 0)),
            user_segments={UserSegment.NEW_USERS, UserSegment.FREQUENT_BUYERS},
            max_radius_km=3.0,
            is_active=True,
        )
        self.repo.save(promo)

        # Act
        response = self.client.get("/api/flash-promos/active/")

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data), 1)

        promo_data = response_data[0]
        required_fields = [
            "id",
            "product_id",
            "store_id",
            "promo_price",
            "time_range",
            "user_segments",
            "is_active",
            "created_at",
        ]

        for field in required_fields:
            self.assertIn(field, promo_data)

        # Check specific field formats
        self.assertIsInstance(promo_data["id"], str)
        self.assertIsInstance(promo_data["product_id"], str)
        self.assertIsInstance(promo_data["store_id"], str)
        self.assertIsInstance(promo_data["promo_price"], dict)
        self.assertIsInstance(promo_data["time_range"], dict)
        self.assertIsInstance(promo_data["user_segments"], list)
        self.assertIsInstance(promo_data["is_active"], bool)
        self.assertIsInstance(promo_data["created_at"], str)
