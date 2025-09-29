"""Tests for DjangoReservationRepository."""
# Standard Python Libraries
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

# Third-Party Libraries
from django.utils import timezone
import pytest

# Local Libraries
from models.models import ReservationModel
from src.domain.entities.reservation import Reservation
from src.infrastructure.repositories.django_reservation_repository import (
    DjangoReservationRepository,
)


class TestDjangoReservationRepository:
    """Test cases for DjangoReservationRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repository = DjangoReservationRepository()

        # Create test data
        self.reservation_id = uuid4()
        self.product_id = uuid4()
        self.user_id = uuid4()
        self.flash_promo_id = uuid4()
        self.created_at = timezone.now()
        self.expires_at = timezone.now() + timedelta(minutes=15)

        self.reservation = Reservation(
            id=self.reservation_id,
            product_id=self.product_id,
            user_id=self.user_id,
            flash_promo_id=self.flash_promo_id,
            created_at=self.created_at,
            expires_at=self.expires_at,
        )

    def test_save_new_reservation(self):
        """Test saving a new reservation."""
        # Arrange
        with patch.object(ReservationModel.objects, "get") as mock_get:
            mock_get.side_effect = ReservationModel.DoesNotExist()
            with patch.object(
                self.repository, "_create_model_from_entity"
            ) as mock_create:
                with patch.object(self.repository, "_entity_from_model") as mock_entity:
                    mock_model = Mock()
                    mock_create.return_value = mock_model
                    mock_entity.return_value = self.reservation

                    # Act
                    result = self.repository.save(self.reservation)

                    # Assert
                    assert result == self.reservation
                    mock_create.assert_called_once_with(self.reservation)
                    mock_model.save.assert_called_once()
                    mock_entity.assert_called_once_with(mock_model)

    def test_save_existing_reservation(self):
        """Test saving an existing reservation."""
        # Arrange
        mock_model = Mock()
        with patch.object(ReservationModel.objects, "get") as mock_get:
            mock_get.return_value = mock_model
            with patch.object(
                self.repository, "_update_model_from_entity"
            ) as mock_update:
                with patch.object(self.repository, "_entity_from_model") as mock_entity:
                    mock_entity.return_value = self.reservation

                    # Act
                    result = self.repository.save(self.reservation)

                    # Assert
                    assert result == self.reservation
                    mock_get.assert_called_once_with(id=self.reservation_id)
                    mock_update.assert_called_once_with(mock_model, self.reservation)
                    mock_model.save.assert_called_once()
                    mock_entity.assert_called_once_with(mock_model)

    def test_get_by_id_success(self):
        """Test getting reservation by ID successfully."""
        # Arrange
        mock_model = Mock()
        with patch.object(ReservationModel.objects, "get") as mock_get:
            mock_get.return_value = mock_model
            with patch.object(self.repository, "_entity_from_model") as mock_entity:
                mock_entity.return_value = self.reservation

                # Act
                result = self.repository.get_by_id(self.reservation_id)

                # Assert
                assert result == self.reservation
                mock_get.assert_called_once_with(id=self.reservation_id)
                mock_entity.assert_called_once_with(mock_model)

    def test_get_by_id_not_found(self):
        """Test getting reservation by ID when not found."""
        # Arrange
        with patch.object(ReservationModel.objects, "get") as mock_get:
            mock_get.side_effect = ReservationModel.DoesNotExist()

            # Act
            result = self.repository.get_by_id(self.reservation_id)

            # Assert
            assert result is None
            mock_get.assert_called_once_with(id=self.reservation_id)

    def test_get_by_product(self):
        """Test getting reservations by product."""
        # Arrange
        mock_models = [Mock(), Mock()]
        with patch.object(ReservationModel.objects, "filter") as mock_filter:
            mock_filter.return_value = mock_models
            with patch.object(self.repository, "_entity_from_model") as mock_entity:
                mock_entity.side_effect = [self.reservation, self.reservation]

                # Act
                result = self.repository.get_by_product(self.product_id)

                # Assert
                assert len(result) == 2
                assert all(r == self.reservation for r in result)
                mock_filter.assert_called_once_with(product_id=self.product_id)
                assert mock_entity.call_count == 2

    def test_get_by_user(self):
        """Test getting reservations by user."""
        # Arrange
        mock_models = [Mock()]
        with patch.object(ReservationModel.objects, "filter") as mock_filter:
            mock_filter.return_value = mock_models
            with patch.object(self.repository, "_entity_from_model") as mock_entity:
                mock_entity.return_value = self.reservation

                # Act
                result = self.repository.get_by_user(self.user_id)

                # Assert
                assert len(result) == 1
                assert result[0] == self.reservation
                mock_filter.assert_called_once_with(user_id=self.user_id)
                mock_entity.assert_called_once_with(mock_models[0])

    def test_get_active_reservations(self):
        """Test getting active reservations."""
        # Arrange
        mock_models = [Mock(), Mock()]
        now = timezone.now()
        with patch.object(timezone, "now") as mock_now:
            mock_now.return_value = now
            with patch.object(ReservationModel.objects, "filter") as mock_filter:
                mock_filter.return_value = mock_models
                with patch.object(self.repository, "_entity_from_model") as mock_entity:
                    mock_entity.side_effect = [self.reservation, self.reservation]

                    # Act
                    result = self.repository.get_active_reservations()

                    # Assert
                    assert len(result) == 2
                    assert all(r == self.reservation for r in result)
                    mock_filter.assert_called_once_with(expires_at__gt=now)
                    assert mock_entity.call_count == 2

    def test_get_expired_reservations(self):
        """Test getting expired reservations."""
        # Arrange
        mock_models = [Mock()]
        now = timezone.now()
        with patch.object(timezone, "now") as mock_now:
            mock_now.return_value = now
            with patch.object(ReservationModel.objects, "filter") as mock_filter:
                mock_filter.return_value = mock_models
                with patch.object(self.repository, "_entity_from_model") as mock_entity:
                    mock_entity.return_value = self.reservation

                    # Act
                    result = self.repository.get_expired_reservations()

                    # Assert
                    assert len(result) == 1
                    assert result[0] == self.reservation
                    mock_filter.assert_called_once_with(expires_at__lte=now)
                    mock_entity.assert_called_once_with(mock_models[0])

    def test_delete_success(self):
        """Test successful deletion of reservation."""
        # Arrange
        mock_model = Mock()
        with patch.object(ReservationModel.objects, "get") as mock_get:
            mock_get.return_value = mock_model
            with patch.object(mock_model, "delete") as mock_delete:
                # Act
                result = self.repository.delete(self.reservation_id)

                # Assert
                assert result is True
                mock_get.assert_called_once_with(id=self.reservation_id)
                mock_delete.assert_called_once()

    def test_delete_not_found(self):
        """Test deletion when reservation not found."""
        # Arrange
        with patch.object(ReservationModel.objects, "get") as mock_get:
            mock_get.side_effect = ReservationModel.DoesNotExist()

            # Act
            result = self.repository.delete(self.reservation_id)

            # Assert
            assert result is False
            mock_get.assert_called_once_with(id=self.reservation_id)

    def test_delete_expired(self):
        """Test deleting expired reservations."""
        # Arrange
        now = timezone.now()
        with patch.object(timezone, "now") as mock_now:
            mock_now.return_value = now
            with patch.object(ReservationModel.objects, "filter") as mock_filter:
                mock_queryset = Mock()
                mock_filter.return_value = mock_queryset
                mock_queryset.delete.return_value = (5, {"models.ReservationModel": 5})

                # Act
                result = self.repository.delete_expired()

                # Assert
                assert result == 5
                mock_filter.assert_called_once_with(expires_at__lte=now)
                mock_queryset.delete.assert_called_once()

    def test_exists_active_for_product_true(self):
        """Test checking active reservation exists for product."""
        # Arrange
        now = timezone.now()
        with patch.object(timezone, "now") as mock_now:
            mock_now.return_value = now
            with patch.object(ReservationModel.objects, "filter") as mock_filter:
                mock_queryset = Mock()
                mock_filter.return_value = mock_queryset
                mock_queryset.exists.return_value = True

                # Act
                result = self.repository.exists_active_for_product(self.product_id)

                # Assert
                assert result is True
                mock_filter.assert_called_once_with(
                    product_id=self.product_id, expires_at__gt=now
                )
                mock_queryset.exists.assert_called_once()

    def test_exists_active_for_product_false(self):
        """Test checking active reservation does not exist for product."""
        # Arrange
        now = timezone.now()
        with patch.object(timezone, "now") as mock_now:
            mock_now.return_value = now
            with patch.object(ReservationModel.objects, "filter") as mock_filter:
                mock_queryset = Mock()
                mock_filter.return_value = mock_queryset
                mock_queryset.exists.return_value = False

                # Act
                result = self.repository.exists_active_for_product(self.product_id)

                # Assert
                assert result is False
                mock_filter.assert_called_once_with(
                    product_id=self.product_id, expires_at__gt=now
                )
                mock_queryset.exists.assert_called_once()

    def test_create_model_from_entity(self):
        """Test creating model from entity."""
        # Act
        result = self.repository._create_model_from_entity(self.reservation)

        # Assert
        assert result.id == self.reservation_id
        assert result.product_id == self.product_id
        assert result.user_id == self.user_id
        assert result.created_at == self.created_at
        assert result.expires_at == self.expires_at

    def test_update_model_from_entity(self):
        """Test updating model from entity."""
        # Arrange
        mock_model = Mock()

        # Act
        self.repository._update_model_from_entity(mock_model, self.reservation)

        # Assert
        assert mock_model.product_id == self.product_id
        assert mock_model.user_id == self.user_id
        assert mock_model.expires_at == self.expires_at

    def test_entity_from_model(self):
        """Test creating entity from model."""
        # Arrange
        mock_model = Mock()
        mock_model.id = self.reservation_id
        mock_model.product_id = self.product_id
        mock_model.user_id = self.user_id
        mock_model.created_at = self.created_at
        mock_model.expires_at = self.expires_at

        # Act
        result = self.repository._entity_from_model(mock_model)

        # Assert
        assert result.id == self.reservation_id
        assert result.product_id == self.product_id
        assert result.user_id == self.user_id
        assert result.created_at == self.created_at
        assert result.expires_at == self.expires_at

    def test_save_with_exception(self):
        """Test save method with exception handling."""
        # Arrange
        with patch.object(ReservationModel.objects, "get") as mock_get:
            mock_get.side_effect = Exception("Database error")

            # Act & Assert
            with pytest.raises(Exception, match="Database error"):
                self.repository.save(self.reservation)

    def test_get_by_product_empty_result(self):
        """Test getting reservations by product with empty result."""
        # Arrange
        with patch.object(ReservationModel.objects, "filter") as mock_filter:
            mock_filter.return_value = []

            # Act
            result = self.repository.get_by_product(self.product_id)

            # Assert
            assert result == []
            mock_filter.assert_called_once_with(product_id=self.product_id)

    def test_get_by_user_empty_result(self):
        """Test getting reservations by user with empty result."""
        # Arrange
        with patch.object(ReservationModel.objects, "filter") as mock_filter:
            mock_filter.return_value = []

            # Act
            result = self.repository.get_by_user(self.user_id)

            # Assert
            assert result == []
            mock_filter.assert_called_once_with(user_id=self.user_id)

    def test_get_active_reservations_empty_result(self):
        """Test getting active reservations with empty result."""
        # Arrange
        now = timezone.now()
        with patch.object(timezone, "now") as mock_now:
            mock_now.return_value = now
            with patch.object(ReservationModel.objects, "filter") as mock_filter:
                mock_filter.return_value = []

                # Act
                result = self.repository.get_active_reservations()

                # Assert
                assert result == []
                mock_filter.assert_called_once_with(expires_at__gt=now)

    def test_get_expired_reservations_empty_result(self):
        """Test getting expired reservations with empty result."""
        # Arrange
        now = timezone.now()
        with patch.object(timezone, "now") as mock_now:
            mock_now.return_value = now
            with patch.object(ReservationModel.objects, "filter") as mock_filter:
                mock_filter.return_value = []

                # Act
                result = self.repository.get_expired_reservations()

                # Assert
                assert result == []
                mock_filter.assert_called_once_with(expires_at__lte=now)

    def test_delete_expired_no_expired_reservations(self):
        """Test deleting expired reservations when none exist."""
        # Arrange
        now = timezone.now()
        with patch.object(timezone, "now") as mock_now:
            mock_now.return_value = now
            with patch.object(ReservationModel.objects, "filter") as mock_filter:
                mock_queryset = Mock()
                mock_filter.return_value = mock_queryset
                mock_queryset.delete.return_value = (0, {})

                # Act
                result = self.repository.delete_expired()

                # Assert
                assert result == 0
                mock_filter.assert_called_once_with(expires_at__lte=now)
                mock_queryset.delete.assert_called_once()
