# Standard Python Libraries
from datetime import datetime, time, timedelta
from decimal import Decimal
import os
from uuid import uuid4

# Third-Party Libraries
import django
from django.test import TestCase
from django.test.client import Client
import pytest

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.product import Product
from src.domain.entities.reservation import Reservation
from src.domain.entities.store import Store
from src.domain.entities.user import User
from src.domain.value_objects.location import Location
from src.domain.value_objects.price import Price
from src.domain.value_objects.time_range import TimeRange
from src.domain.value_objects.user_segment import UserSegment

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flash_promos.settings")
django.setup()


@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    location = Location(Decimal("40.7128"), Decimal("-74.0060"))  # NYC
    return User(
        email="test@example.com",
        name="Test User",
        location=location,
        total_purchases=5,
        total_spent=500.0,
    )


@pytest.fixture
def sample_store():
    """Create a sample store for testing."""
    location = Location(Decimal("40.7589"), Decimal("-73.9851"))  # Times Square
    return Store(name="Test Store", location=location)


@pytest.fixture
def sample_product():
    """Create a sample product for testing."""
    return Product(
        name="Test Product",
        description="A test product",
        original_price=Price(Decimal("100.00")),
        stock_quantity=10,
    )


@pytest.fixture
def sample_flash_promo(sample_product, sample_store):
    """Create a sample flash promo for testing."""
    promo_price = Price(Decimal("50.00"))
    time_range = TimeRange(time(17, 0), time(19, 0))  # 5 PM to 7 PM
    user_segments = {UserSegment.NEW_USERS, UserSegment.FREQUENT_BUYERS}

    return FlashPromo(
        product_id=sample_product.id,
        store_id=sample_store.id,
        promo_price=promo_price,
        time_range=time_range,
        user_segments=user_segments,
        max_radius_km=2.0,
    )


@pytest.fixture
def sample_reservation(sample_user, sample_product, sample_flash_promo):
    """Create a sample reservation for testing."""
    return Reservation(
        product_id=sample_product.id,
        user_id=sample_user.id,
        flash_promo_id=sample_flash_promo.id,
    )


@pytest.fixture
def sample_price():
    """Create a sample price for testing."""
    return Price(Decimal("99.99"))


@pytest.fixture
def sample_location():
    """Create a sample location for testing."""
    return Location(Decimal("40.7128"), Decimal("-74.0060"))


@pytest.fixture
def sample_time_range():
    """Create a sample time range for testing."""
    return TimeRange(time(9, 0), time(17, 0))  # 9 AM to 5 PM


@pytest.fixture
def sample_user_segments():
    """Create sample user segments for testing."""
    return {UserSegment.NEW_USERS, UserSegment.FREQUENT_BUYERS}


@pytest.fixture
def mock_redis():
    """Mock Redis for testing."""
    # Standard Python Libraries
    from unittest.mock import Mock

    # Third-Party Libraries
    import redis

    mock_redis = Mock(spec=redis.Redis)
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.exists.return_value = False
    mock_redis.ping.return_value = True

    return mock_redis


@pytest.fixture
def mock_celery():
    """Mock Celery for testing."""
    # Standard Python Libraries
    from unittest.mock import Mock

    mock_celery = Mock()
    mock_celery.send_task.return_value.id = "test-task-id"
    mock_celery.AsyncResult.return_value.status = "SUCCESS"
    mock_celery.AsyncResult.return_value.ready.return_value = True
    mock_celery.AsyncResult.return_value.result = {"status": "completed"}

    return mock_celery


class BaseTestCase(TestCase):
    """Base test case with common setup."""

    def setUp(self):
        """Set up test data."""
        self.user = User(
            email="test@example.com",
            name="Test User",
            location=Location(Decimal("40.7128"), Decimal("-74.0060")),
        )

        self.store = Store(
            name="Test Store",
            location=Location(Decimal("40.7589"), Decimal("-73.9851")),
        )

        self.product = Product(
            name="Test Product",
            description="A test product",
            original_price=Price(Decimal("100.00")),
        )

        self.flash_promo = FlashPromo(
            product_id=self.product.id,
            store_id=self.store.id,
            promo_price=Price(Decimal("50.00")),
            time_range=TimeRange(time(17, 0), time(19, 0)),
            user_segments={UserSegment.NEW_USERS},
        )
