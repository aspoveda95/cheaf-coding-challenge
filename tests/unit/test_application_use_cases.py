# Standard Python Libraries
from datetime import datetime, time, timedelta
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

# Third-Party Libraries
import pytest

# Local Libraries
from src.application.use_cases.activate_flash_promo import ActivateFlashPromoUseCase
from src.application.use_cases.create_flash_promo import CreateFlashPromoUseCase
from src.application.use_cases.process_purchase import ProcessPurchaseUseCase
from src.application.use_cases.reserve_product import ReserveProductUseCase
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.reservation import Reservation
from src.domain.entities.user import User
from src.domain.value_objects.price import Price
from src.domain.value_objects.time_range import TimeRange
from src.domain.value_objects.user_segment import UserSegment


class TestCreateFlashPromoUseCase:
    """Test CreateFlashPromoUseCase."""

    def test_create_flash_promo_success(self):
        """Test successful flash promo creation."""
        # Mock repositories
        mock_flash_promo_repo = Mock()
        mock_user_repo = Mock()

        # Mock save method
        created_promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(Decimal("50.00")),
            time_range=TimeRange(time(17, 0), time(19, 0)),
            user_segments={UserSegment.NEW_USERS},
        )
        mock_flash_promo_repo.save.return_value = created_promo

        # Create use case
        use_case = CreateFlashPromoUseCase(mock_flash_promo_repo, mock_user_repo)

        # Execute
        result = use_case.execute(
            product_id=created_promo.product_id,
            store_id=created_promo.store_id,
            promo_price=created_promo.promo_price,
            time_range=created_promo.time_range,
            user_segments=created_promo.user_segments,
            max_radius_km=2.0,
        )

        # Assertions
        assert result == created_promo
        mock_flash_promo_repo.save.assert_called_once()

    def test_create_flash_promo_negative_radius(self):
        """Test flash promo creation with negative radius."""
        mock_flash_promo_repo = Mock()
        mock_user_repo = Mock()

        use_case = CreateFlashPromoUseCase(mock_flash_promo_repo, mock_user_repo)

        with pytest.raises(ValueError, match="Max radius cannot be negative"):
            use_case.execute(
                product_id=uuid4(),
                store_id=uuid4(),
                promo_price=Price(Decimal("50.00")),
                time_range=TimeRange(time(17, 0), time(19, 0)),
                user_segments={UserSegment.NEW_USERS},
                max_radius_km=-1.0,
            )

    def test_create_flash_promo_empty_segments(self):
        """Test flash promo creation with empty segments."""
        mock_flash_promo_repo = Mock()
        mock_user_repo = Mock()

        use_case = CreateFlashPromoUseCase(mock_flash_promo_repo, mock_user_repo)

        with pytest.raises(
            ValueError, match="At least one user segment must be specified"
        ):
            use_case.execute(
                product_id=uuid4(),
                store_id=uuid4(),
                promo_price=Price(Decimal("50.00")),
                time_range=TimeRange(time(17, 0), time(19, 0)),
                user_segments=set(),
                max_radius_km=2.0,
            )


class TestActivateFlashPromoUseCase:
    """Test ActivateFlashPromoUseCase."""

    def test_activate_flash_promo_success(self):
        """Test successful flash promo activation."""
        # Mock repositories
        mock_flash_promo_repo = Mock()
        mock_user_repo = Mock()

        # Mock promo
        promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(Decimal("50.00")),
            time_range=TimeRange(time(17, 0), time(19, 0)),
            user_segments={UserSegment.NEW_USERS},
        )
        mock_flash_promo_repo.get_by_id.return_value = promo
        mock_flash_promo_repo.save.return_value = promo

        # Create use case
        use_case = ActivateFlashPromoUseCase(mock_flash_promo_repo, mock_user_repo)

        # Execute
        result = use_case.execute(promo.id)

        # Assertions
        assert result == promo
        assert promo.is_active is True
        mock_flash_promo_repo.get_by_id.assert_called_once_with(promo.id)
        mock_flash_promo_repo.save.assert_called_once_with(promo)

    def test_activate_flash_promo_not_found(self):
        """Test flash promo activation when promo not found."""
        mock_flash_promo_repo = Mock()
        mock_user_repo = Mock()
        mock_flash_promo_repo.get_by_id.return_value = None

        use_case = ActivateFlashPromoUseCase(mock_flash_promo_repo, mock_user_repo)

        with pytest.raises(ValueError, match="Flash promo .* not found"):
            use_case.execute(uuid4())

    def test_get_active_promos(self):
        """Test getting active promos."""
        mock_flash_promo_repo = Mock()
        mock_user_repo = Mock()

        # Mock active promos - use a time range that's always active
        # Standard Python Libraries
        from datetime import datetime, time

        now = datetime.now()
        start_time = time(now.hour - 1, now.minute)
        end_time = time(now.hour + 1, now.minute)

        active_promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(Decimal("50.00")),
            time_range=TimeRange(start_time, end_time),
            user_segments={UserSegment.NEW_USERS},
            is_active=True,  # Explicitly set as active
        )
        mock_flash_promo_repo.get_active_promos.return_value = [active_promo]

        use_case = ActivateFlashPromoUseCase(mock_flash_promo_repo, mock_user_repo)

        result = use_case.get_active_promos()

        assert len(result) == 1
        assert result[0] == active_promo
        mock_flash_promo_repo.get_active_promos.assert_called_once()

    def test_get_eligible_users_for_promo(self):
        """Test getting eligible users for a promo."""
        mock_flash_promo_repo = Mock()
        mock_user_repo = Mock()

        # Mock promo - use a time range that's always active
        # Standard Python Libraries
        from datetime import datetime, time

        now = datetime.now()
        start_time = time(now.hour - 1, now.minute)
        end_time = time(now.hour + 1, now.minute)

        promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(Decimal("50.00")),
            time_range=TimeRange(start_time, end_time),
            user_segments={UserSegment.NEW_USERS},
            is_active=True,  # Explicitly set as active
        )
        mock_flash_promo_repo.get_by_id.return_value = promo

        # Mock users
        eligible_users = [
            User(email="user1@example.com", name="User 1"),
            User(email="user2@example.com", name="User 2"),
        ]
        mock_user_repo.get_users_by_segments.return_value = eligible_users

        use_case = ActivateFlashPromoUseCase(mock_flash_promo_repo, mock_user_repo)

        result = use_case.get_eligible_users_for_promo(promo.id)

        assert len(result) == 2
        assert result == eligible_users
        mock_flash_promo_repo.get_by_id.assert_called_once_with(promo.id)
        mock_user_repo.get_users_by_segments.assert_called_once_with(
            promo.user_segments
        )


class TestReserveProductUseCase:
    """Test ReserveProductUseCase."""

    def test_reserve_product_success(self):
        """Test successful product reservation."""
        mock_flash_promo_repo = Mock()
        mock_reservation_repo = Mock()

        # Mock flash promo - use a time range that's always active
        # Standard Python Libraries
        from datetime import datetime, time

        now = datetime.now()
        start_time = time(now.hour - 1, now.minute)
        end_time = time(now.hour + 1, now.minute)

        promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(Decimal("50.00")),
            time_range=TimeRange(start_time, end_time),
            user_segments={UserSegment.NEW_USERS},
            is_active=True,  # Explicitly set as active
        )
        mock_flash_promo_repo.get_by_id.return_value = promo

        # Mock reservation
        reservation = Reservation(
            product_id=promo.product_id, user_id=uuid4(), flash_promo_id=promo.id
        )
        mock_reservation_repo.save.return_value = reservation
        mock_reservation_repo.exists_active_for_product.return_value = False

        use_case = ReserveProductUseCase(mock_flash_promo_repo, mock_reservation_repo)

        result = use_case.execute(
            product_id=promo.product_id, user_id=uuid4(), flash_promo_id=promo.id
        )

        assert result == reservation
        mock_flash_promo_repo.get_by_id.assert_called_once_with(promo.id)
        mock_reservation_repo.save.assert_called_once()

    def test_reserve_product_promo_not_found(self):
        """Test product reservation when promo not found."""
        mock_flash_promo_repo = Mock()
        mock_reservation_repo = Mock()
        mock_flash_promo_repo.get_by_id.return_value = None

        use_case = ReserveProductUseCase(mock_flash_promo_repo, mock_reservation_repo)

        with pytest.raises(ValueError, match="Flash promo .* not found"):
            use_case.execute(
                product_id=uuid4(), user_id=uuid4(), flash_promo_id=uuid4()
            )

    def test_reserve_product_promo_not_active(self):
        """Test product reservation when promo is not active."""
        mock_flash_promo_repo = Mock()
        mock_reservation_repo = Mock()

        # Mock inactive promo
        promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(Decimal("50.00")),
            time_range=TimeRange(time(22, 0), time(23, 0)),  # Night time
            user_segments={UserSegment.NEW_USERS},
        )
        mock_flash_promo_repo.get_by_id.return_value = promo

        use_case = ReserveProductUseCase(mock_flash_promo_repo, mock_reservation_repo)

        with pytest.raises(ValueError, match="Flash promo .* is not currently active"):
            use_case.execute(
                product_id=promo.product_id, user_id=uuid4(), flash_promo_id=promo.id
            )

    def test_reserve_product_already_reserved(self):
        """Test product reservation when product is already reserved."""
        mock_flash_promo_repo = Mock()
        mock_reservation_repo = Mock()

        # Mock active promo - use a time range that's always active
        # Standard Python Libraries
        from datetime import datetime, time

        now = datetime.now()
        start_time = time(now.hour - 1, now.minute)
        end_time = time(now.hour + 1, now.minute)

        promo = FlashPromo(
            product_id=uuid4(),
            store_id=uuid4(),
            promo_price=Price(Decimal("50.00")),
            time_range=TimeRange(start_time, end_time),
            user_segments={UserSegment.NEW_USERS},
            is_active=True,  # Explicitly set as active
        )
        mock_flash_promo_repo.get_by_id.return_value = promo
        mock_reservation_repo.exists_active_for_product.return_value = True

        use_case = ReserveProductUseCase(mock_flash_promo_repo, mock_reservation_repo)

        result = use_case.execute(
            product_id=promo.product_id, user_id=uuid4(), flash_promo_id=promo.id
        )

        assert result is None


class TestProcessPurchaseUseCase:
    """Test ProcessPurchaseUseCase."""

    def test_process_purchase_success(self):
        """Test successful purchase processing."""
        mock_flash_promo_repo = Mock()
        mock_reservation_repo = Mock()
        mock_user_repo = Mock()

        # Mock reservation
        reservation = Reservation(
            product_id=uuid4(), user_id=uuid4(), flash_promo_id=uuid4()
        )
        mock_reservation_repo.get_by_id.return_value = reservation

        # Mock flash promo - use a time range that's always active
        # Standard Python Libraries
        from datetime import datetime, time

        now = datetime.now()
        start_time = time(now.hour - 1, now.minute)
        end_time = time(now.hour + 1, now.minute)

        promo = FlashPromo(
            product_id=reservation.product_id,
            store_id=uuid4(),
            promo_price=Price(Decimal("50.00")),
            time_range=TimeRange(start_time, end_time),
            user_segments={UserSegment.NEW_USERS},
            is_active=True,  # Explicitly set as active
        )
        mock_flash_promo_repo.get_by_id.return_value = promo

        # Mock user
        user = User(email="test@example.com", name="Test User")
        mock_user_repo.get_by_id.return_value = user
        mock_user_repo.save.return_value = user

        use_case = ProcessPurchaseUseCase(
            mock_flash_promo_repo, mock_reservation_repo, mock_user_repo
        )

        result = use_case.execute(reservation.id, reservation.user_id)

        assert result is True
        mock_reservation_repo.get_by_id.assert_called_once_with(reservation.id)
        mock_flash_promo_repo.get_by_id.assert_called_once_with(
            reservation.flash_promo_id
        )
        mock_user_repo.get_by_id.assert_called_once_with(reservation.user_id)
        mock_user_repo.save.assert_called_once()
        mock_reservation_repo.delete.assert_called_once_with(reservation.id)

    def test_process_purchase_reservation_not_found(self):
        """Test purchase processing when reservation not found."""
        mock_flash_promo_repo = Mock()
        mock_reservation_repo = Mock()
        mock_user_repo = Mock()
        mock_reservation_repo.get_by_id.return_value = None

        use_case = ProcessPurchaseUseCase(
            mock_flash_promo_repo, mock_reservation_repo, mock_user_repo
        )

        with pytest.raises(ValueError, match="Reservation .* not found"):
            use_case.execute(uuid4(), uuid4())

    def test_process_purchase_reservation_expired(self):
        """Test purchase processing when reservation is expired."""
        mock_flash_promo_repo = Mock()
        mock_reservation_repo = Mock()
        mock_user_repo = Mock()

        # Mock expired reservation
        reservation = Reservation(
            product_id=uuid4(),
            user_id=uuid4(),
            flash_promo_id=uuid4(),
            expires_at=datetime.now() - timedelta(minutes=5),  # Expired
        )
        mock_reservation_repo.get_by_id.return_value = reservation

        use_case = ProcessPurchaseUseCase(
            mock_flash_promo_repo, mock_reservation_repo, mock_user_repo
        )

        with pytest.raises(ValueError, match="Reservation has expired"):
            use_case.execute(reservation.id, reservation.user_id)

    def test_process_purchase_wrong_user(self):
        """Test purchase processing with wrong user."""
        mock_flash_promo_repo = Mock()
        mock_reservation_repo = Mock()
        mock_user_repo = Mock()

        # Mock reservation
        reservation = Reservation(
            product_id=uuid4(), user_id=uuid4(), flash_promo_id=uuid4()
        )
        mock_reservation_repo.get_by_id.return_value = reservation

        use_case = ProcessPurchaseUseCase(
            mock_flash_promo_repo, mock_reservation_repo, mock_user_repo
        )

        with pytest.raises(
            ValueError, match="Reservation does not belong to this user"
        ):
            use_case.execute(reservation.id, uuid4())  # Different user ID

    def test_get_purchase_price(self):
        """Test getting purchase price for a reservation."""
        mock_flash_promo_repo = Mock()
        mock_reservation_repo = Mock()
        mock_user_repo = Mock()

        # Mock reservation
        reservation = Reservation(
            product_id=uuid4(), user_id=uuid4(), flash_promo_id=uuid4()
        )
        mock_reservation_repo.get_by_id.return_value = reservation

        # Mock flash promo - use a time range that's always active
        # Standard Python Libraries
        from datetime import datetime, time

        now = datetime.now()
        start_time = time(now.hour - 1, now.minute)
        end_time = time(now.hour + 1, now.minute)

        promo = FlashPromo(
            product_id=reservation.product_id,
            store_id=uuid4(),
            promo_price=Price(Decimal("50.00")),
            time_range=TimeRange(start_time, end_time),
            user_segments={UserSegment.NEW_USERS},
            is_active=True,  # Explicitly set as active
        )
        mock_flash_promo_repo.get_by_id.return_value = promo

        use_case = ProcessPurchaseUseCase(
            mock_flash_promo_repo, mock_reservation_repo, mock_user_repo
        )

        result = use_case.get_purchase_price(reservation.id)

        assert result == promo.promo_price
        mock_reservation_repo.get_by_id.assert_called_once_with(reservation.id)
        mock_flash_promo_repo.get_by_id.assert_called_once_with(
            reservation.flash_promo_id
        )
