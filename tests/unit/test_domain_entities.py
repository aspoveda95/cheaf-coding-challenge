# Standard Python Libraries
from datetime import datetime, time, timedelta
from decimal import Decimal
from uuid import uuid4

# Third-Party Libraries
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


class TestUser:
    """Test User entity."""

    def test_user_creation(self):
        """Test user creation with basic attributes."""
        user = User(
            email="test@example.com",
            name="Test User",
            location=Location(Decimal("40.7128"), Decimal("-74.0060")),
        )

        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.location is not None
        assert user.total_purchases == 0
        assert user.total_spent == 0.0
        assert len(user.segments) == 0

    def test_user_is_new_user(self):
        """Test new user detection."""
        # Recent user
        recent_user = User(
            email="recent@example.com",
            name="Recent User",
            created_at=datetime.now() - timedelta(days=15),
        )
        assert recent_user.is_new_user()

        # Old user
        old_user = User(
            email="old@example.com",
            name="Old User",
            created_at=datetime.now() - timedelta(days=60),
        )
        assert not old_user.is_new_user()

    def test_user_is_frequent_buyer(self):
        """Test frequent buyer detection."""
        # Frequent buyer
        frequent_user = User(
            email="frequent@example.com",
            name="Frequent User",
            total_purchases=10,
            last_purchase_at=datetime.now() - timedelta(days=5),
        )
        assert frequent_user.is_frequent_buyer()

        # Not frequent buyer
        infrequent_user = User(
            email="infrequent@example.com",
            name="Infrequent User",
            total_purchases=2,
            last_purchase_at=datetime.now() - timedelta(days=5),
        )
        assert not infrequent_user.is_frequent_buyer()

    def test_user_is_vip_customer(self):
        """Test VIP customer detection."""
        # VIP customer
        vip_user = User(email="vip@example.com", name="VIP User", total_spent=1500.0)
        assert vip_user.is_vip_customer()

        # Not VIP customer
        regular_user = User(
            email="regular@example.com", name="Regular User", total_spent=500.0
        )
        assert not regular_user.is_vip_customer()

    def test_user_segments(self):
        """Test user segment management."""
        user = User(email="test@example.com", name="Test User")

        # Add segments
        user.add_segment(UserSegment.NEW_USERS)
        user.add_segment(UserSegment.FREQUENT_BUYERS)

        assert user.has_segment(UserSegment.NEW_USERS)
        assert user.has_segment(UserSegment.FREQUENT_BUYERS)
        assert len(user.segments) == 2

        # Remove segment
        user.remove_segment(UserSegment.NEW_USERS)
        assert not user.has_segment(UserSegment.NEW_USERS)
        assert user.has_segment(UserSegment.FREQUENT_BUYERS)
        assert len(user.segments) == 1

    def test_user_record_purchase(self):
        """Test recording a purchase."""
        user = User(email="test@example.com", name="Test User")
        initial_purchases = user.total_purchases
        initial_spent = user.total_spent

        user.record_purchase(100.0)

        assert user.total_purchases == initial_purchases + 1
        assert user.total_spent == initial_spent + 100.0
        assert user.last_purchase_at is not None


class TestStore:
    """Test Store entity."""

    def test_store_creation(self):
        """Test store creation."""
        location = Location(Decimal("40.7589"), Decimal("-73.9851"))
        store = Store(name="Test Store", location=location)

        assert store.name == "Test Store"
        assert store.location == location
        assert store.is_active is True

    def test_store_activation_deactivation(self):
        """Test store activation and deactivation."""
        store = Store(name="Test Store")

        # Deactivate
        store.deactivate()
        assert not store.is_active

        # Activate
        store.activate()
        assert store.is_active


class TestProduct:
    """Test Product entity."""

    def test_product_creation(self):
        """Test product creation."""
        price = Price(Decimal("99.99"))
        product = Product(
            name="Test Product",
            description="A test product",
            original_price=price,
            stock_quantity=10,
        )

        assert product.name == "Test Product"
        assert product.original_price == price
        assert product.stock_quantity == 10
        assert product.is_active is True

    def test_product_stock_management(self):
        """Test product stock management."""
        product = Product(name="Test Product", stock_quantity=10)

        # Reduce stock
        product.reduce_stock(3)
        assert product.stock_quantity == 7

        # Add stock
        product.add_stock(5)
        assert product.stock_quantity == 12

        # Test insufficient stock
        with pytest.raises(ValueError):
            product.reduce_stock(20)

    def test_product_availability(self):
        """Test product availability."""
        # Available product
        available_product = Product(name="Available", stock_quantity=5)
        assert available_product.is_available()

        # Out of stock product
        out_of_stock = Product(name="Out of Stock", stock_quantity=0)
        assert not out_of_stock.is_available()

        # Inactive product
        inactive_product = Product(name="Inactive", stock_quantity=5)
        inactive_product.deactivate()
        assert not inactive_product.is_available()


class TestFlashPromo:
    """Test FlashPromo entity."""

    def test_flash_promo_creation(self):
        """Test flash promo creation."""
        promo_price = Price(Decimal("50.00"))
        time_range = TimeRange(time(17, 0), time(19, 0))
        user_segments = {UserSegment.NEW_USERS, UserSegment.FREQUENT_BUYERS}

        promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=promo_price,
            time_range=time_range,
            user_segments=user_segments,
            max_radius_km=2.0,
        )

        assert promo.promo_price == promo_price
        assert promo.time_range == time_range
        assert promo.user_segments == user_segments
        assert promo.max_radius_km == 2.0
        assert promo.is_active is False

    def test_flash_promo_activation(self):
        """Test flash promo activation and deactivation."""
        promo = FlashPromo(product_id=uuid4(), store_id=uuid4())

        # Deactivate
        promo.deactivate()
        assert not promo.is_active

        # Activate
        promo.activate()
        assert promo.is_active

    def test_flash_promo_currently_active(self):
        """Test flash promo current activation status."""
        # Test with specific time (10:30 AM)
        test_time = datetime.now().replace(hour=10, minute=30, second=0, microsecond=0)

        # Active promo
        active_promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            time_range=TimeRange(time(9, 0), time(17, 0)),
            is_active=True,  # Explicitly set as active
        )
        assert active_promo.is_currently_active(test_time)

        # Inactive promo
        inactive_promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            time_range=TimeRange(time(22, 0), time(23, 0)),
        )
        assert not inactive_promo.is_currently_active(test_time)

    def test_flash_promo_eligibility(self):
        """Test flash promo user eligibility."""
        promo = FlashPromo(
            product_id=uuid4(), store_id=uuid4(), user_segments={UserSegment.NEW_USERS}
        )

        # Eligible user segments
        eligible_segments = {UserSegment.NEW_USERS, UserSegment.FREQUENT_BUYERS}
        assert promo.is_eligible_for_user(eligible_segments)

        # Non-eligible user segments
        non_eligible_segments = {UserSegment.VIP_CUSTOMERS}
        assert not promo.is_eligible_for_user(non_eligible_segments)


class TestReservation:
    """Test Reservation entity."""

    def test_reservation_creation(self):
        """Test reservation creation."""
        reservation = Reservation(
            product_id=uuid4(), user_id=uuid4(), flash_promo_id=uuid4()
        )

        assert reservation.product_id is not None
        assert reservation.user_id is not None
        assert reservation.flash_promo_id is not None
        assert not reservation.is_expired()

    def test_reservation_expiration(self):
        """Test reservation expiration."""
        # Expired reservation
        expired_reservation = Reservation(
            product_id=uuid4(),
            user_id=uuid4(),
            flash_promo_id=uuid4(),
            expires_at=datetime.now() - timedelta(minutes=1),
        )
        assert expired_reservation.is_expired()

        # Active reservation
        active_reservation = Reservation(
            product_id=uuid4(),
            user_id=uuid4(),
            flash_promo_id=uuid4(),
            expires_at=datetime.now() + timedelta(minutes=1),
        )
        assert not active_reservation.is_expired()

    def test_reservation_time_remaining(self):
        """Test reservation time remaining."""
        reservation = Reservation(
            product_id=uuid4(),
            user_id=uuid4(),
            flash_promo_id=uuid4(),
            expires_at=datetime.now() + timedelta(seconds=30),
        )

        time_remaining = reservation.time_remaining_seconds()
        assert 25 <= time_remaining <= 30  # Allow for small time differences

    def test_reservation_extension(self):
        """Test reservation extension."""
        reservation = Reservation(
            product_id=uuid4(), user_id=uuid4(), flash_promo_id=uuid4()
        )

        original_expiry = reservation.expires_at
        reservation.extend_reservation(minutes=5)

        assert reservation.expires_at > original_expiry
