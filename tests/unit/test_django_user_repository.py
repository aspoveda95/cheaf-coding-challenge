"""Tests for DjangoUserRepository."""
# Standard Python Libraries
from decimal import Decimal
from unittest.mock import Mock, patch
from uuid import uuid4

# Third-Party Libraries
import pytest

# Local Libraries
from models.models import UserModel
from src.domain.entities.user import User
from src.domain.value_objects.location import Location
from src.domain.value_objects.user_segment import UserSegment
from src.infrastructure.repositories.django_user_repository import DjangoUserRepository


class TestDjangoUserRepository:
    """Test cases for DjangoUserRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repository = DjangoUserRepository()

        # Create test data
        self.user_id = uuid4()
        self.email = "test@example.com"
        self.name = "Test User"
        self.location = Location(Decimal("40.7128"), Decimal("-74.0060"))
        self.segments = {UserSegment.NEW_USERS, UserSegment.FREQUENT_BUYERS}

        self.user = User(
            id=self.user_id,
            email=self.email,
            name=self.name,
            location=self.location,
            created_at="2023-01-01T00:00:00Z",
            segments=self.segments,
        )

    def test_calculate_distance_same_point(self):
        """Test distance calculation for same point."""
        # Act
        distance = self.repository._calculate_distance(
            40.7128, -74.0060, 40.7128, -74.0060
        )

        # Assert
        assert distance == 0.0

    def test_calculate_distance_different_points(self):
        """Test distance calculation for different points."""
        # Act
        distance = self.repository._calculate_distance(
            40.7128, -74.0060, 40.7589, -73.9851
        )

        # Assert
        assert distance > 0
        assert distance < 100  # Should be reasonable distance in NYC

    def test_calculate_distance_antipodal_points(self):
        """Test distance calculation for antipodal points."""
        # Act
        distance = self.repository._calculate_distance(0, 0, 0, 180)

        # Assert
        # Should be approximately half the Earth's circumference
        assert distance > 19000
        assert distance < 21000

    def test_save_new_user(self):
        """Test saving a new user."""
        # Arrange
        with patch.object(UserModel.objects, "get") as mock_get:
            mock_get.side_effect = UserModel.DoesNotExist()
            with patch.object(
                self.repository, "_create_model_from_entity"
            ) as mock_create:
                with patch.object(self.repository, "_entity_from_model") as mock_entity:
                    mock_model = Mock()
                    mock_create.return_value = mock_model
                    mock_entity.return_value = self.user

                    # Act
                    result = self.repository.save(self.user)

                    # Assert
                    assert result == self.user
                    mock_create.assert_called_once_with(self.user)
                    mock_model.save.assert_called_once()
                    mock_entity.assert_called_once_with(mock_model)

    def test_save_existing_user(self):
        """Test saving an existing user."""
        # Arrange
        mock_model = Mock()
        with patch.object(UserModel.objects, "get") as mock_get:
            mock_get.return_value = mock_model
            with patch.object(
                self.repository, "_update_model_from_entity"
            ) as mock_update:
                with patch.object(self.repository, "_entity_from_model") as mock_entity:
                    mock_entity.return_value = self.user

                    # Act
                    result = self.repository.save(self.user)

                    # Assert
                    assert result == self.user
                    mock_get.assert_called_once_with(id=self.user_id)
                    mock_update.assert_called_once_with(mock_model, self.user)
                    mock_model.save.assert_called_once()
                    mock_entity.assert_called_once_with(mock_model)

    def test_save_with_exception(self):
        """Test save method with exception handling."""
        # Arrange
        with patch.object(UserModel.objects, "get") as mock_get:
            mock_get.side_effect = UserModel.DoesNotExist()
            with patch.object(
                self.repository, "_create_model_from_entity"
            ) as mock_create:
                mock_model = Mock()
                mock_create.return_value = mock_model
                mock_model.save.side_effect = Exception("Database error")

                # Act & Assert
                with pytest.raises(Exception, match="Database error"):
                    self.repository.save(self.user)

    def test_get_by_id_success(self):
        """Test getting user by ID successfully."""
        # Arrange
        mock_model = Mock()
        with patch.object(UserModel.objects, "get") as mock_get:
            mock_get.return_value = mock_model
            with patch.object(self.repository, "_entity_from_model") as mock_entity:
                mock_entity.return_value = self.user

                # Act
                result = self.repository.get_by_id(self.user_id)

                # Assert
                assert result == self.user
                mock_get.assert_called_once_with(id=self.user_id)
                mock_entity.assert_called_once_with(mock_model)

    def test_get_by_id_not_found(self):
        """Test getting user by ID when not found."""
        # Arrange
        with patch.object(UserModel.objects, "get") as mock_get:
            mock_get.side_effect = UserModel.DoesNotExist()

            # Act
            result = self.repository.get_by_id(self.user_id)

            # Assert
            assert result is None
            mock_get.assert_called_once_with(id=self.user_id)

    def test_get_by_email_success(self):
        """Test getting user by email successfully."""
        # Arrange
        mock_model = Mock()
        with patch.object(UserModel.objects, "get") as mock_get:
            mock_get.return_value = mock_model
            with patch.object(self.repository, "_entity_from_model") as mock_entity:
                mock_entity.return_value = self.user

                # Act
                result = self.repository.get_by_email(self.email)

                # Assert
                assert result == self.user
                mock_get.assert_called_once_with(email=self.email)
                mock_entity.assert_called_once_with(mock_model)

    def test_get_by_email_not_found(self):
        """Test getting user by email when not found."""
        # Arrange
        with patch.object(UserModel.objects, "get") as mock_get:
            mock_get.side_effect = UserModel.DoesNotExist()

            # Act
            result = self.repository.get_by_email(self.email)

            # Assert
            assert result is None
            mock_get.assert_called_once_with(email=self.email)

    def test_get_users_by_segments(self):
        """Test getting users by segments."""
        # Arrange
        segments = {UserSegment.NEW_USERS, UserSegment.FREQUENT_BUYERS}
        mock_models = [Mock(), Mock()]
        with patch.object(UserModel.objects, "filter") as mock_filter:
            mock_filter.return_value = mock_models
            with patch.object(self.repository, "_entity_from_model") as mock_entity:
                mock_entity.side_effect = [self.user, self.user]

                # Act
                result = self.repository.get_users_by_segments(segments)

                # Assert
                assert len(result) == 2
                assert all(r == self.user for r in result)
                mock_filter.assert_called_once()
                assert mock_entity.call_count == 2

    def test_get_users_by_location_with_location(self):
        """Test getting users by location with valid location."""
        # Arrange
        radius_km = 10.0
        mock_models = [Mock(), Mock()]
        mock_models[0].latitude = 40.7128
        mock_models[0].longitude = -74.0060
        mock_models[1].latitude = 40.7589
        mock_models[1].longitude = -73.9851

        with patch.object(UserModel.objects, "filter") as mock_filter:
            mock_filter.return_value = mock_models
            with patch.object(self.repository, "_entity_from_model") as mock_entity:
                mock_entity.side_effect = [self.user, self.user]

                # Act
                result = self.repository.get_users_by_location(self.location, radius_km)

                # Assert
                assert len(result) == 2
                assert all(r == self.user for r in result)
                mock_filter.assert_called_once()
                assert mock_entity.call_count == 2

    def test_get_users_by_location_no_location(self):
        """Test getting users by location with no location."""
        # Act
        result = self.repository.get_users_by_location(None, 10.0)

        # Assert
        assert result == []

    def test_get_users_by_segments_and_location_with_location(self):
        """Test getting users by segments and location with valid location."""
        # Arrange
        segments = {UserSegment.NEW_USERS}
        radius_km = 10.0
        mock_models = [Mock()]
        mock_models[0].latitude = 40.7128
        mock_models[0].longitude = -74.0060

        with patch.object(UserModel.objects, "filter") as mock_filter:
            mock_filter.return_value = mock_models
            with patch.object(self.repository, "_entity_from_model") as mock_entity:
                mock_entity.return_value = self.user

                # Act
                result = self.repository.get_users_by_segments_and_location(
                    segments, self.location, radius_km
                )

                # Assert
                assert len(result) == 1
                assert result[0] == self.user
                mock_filter.assert_called_once()
                mock_entity.assert_called_once_with(mock_models[0])

    def test_get_users_by_segments_and_location_no_location(self):
        """Test getting users by segments and location with no location."""
        # Arrange
        segments = {UserSegment.NEW_USERS}
        mock_models = [Mock()]

        with patch.object(UserModel.objects, "filter") as mock_filter:
            mock_filter.return_value = mock_models
            with patch.object(self.repository, "_entity_from_model") as mock_entity:
                mock_entity.return_value = self.user

                # Act
                result = self.repository.get_users_by_segments_and_location(
                    segments, None, 10.0
                )

                # Assert
                assert len(result) == 1
                assert result[0] == self.user
                mock_filter.assert_called_once()
                mock_entity.assert_called_once_with(mock_models[0])

    def test_delete_success(self):
        """Test successful deletion of user."""
        # Arrange
        mock_model = Mock()
        with patch.object(UserModel.objects, "get") as mock_get:
            mock_get.return_value = mock_model
            with patch.object(mock_model, "delete") as mock_delete:
                # Act
                result = self.repository.delete(self.user_id)

                # Assert
                assert result is True
                mock_get.assert_called_once_with(id=self.user_id)
                mock_delete.assert_called_once()

    def test_delete_not_found(self):
        """Test deletion when user not found."""
        # Arrange
        with patch.object(UserModel.objects, "get") as mock_get:
            mock_get.side_effect = UserModel.DoesNotExist()

            # Act
            result = self.repository.delete(self.user_id)

            # Assert
            assert result is False
            mock_get.assert_called_once_with(id=self.user_id)

    def test_exists_true(self):
        """Test exists method when user exists."""
        # Arrange
        with patch.object(UserModel.objects, "filter") as mock_filter:
            mock_queryset = Mock()
            mock_filter.return_value = mock_queryset
            mock_queryset.exists.return_value = True

            # Act
            result = self.repository.exists(self.user_id)

            # Assert
            assert result is True
            mock_filter.assert_called_once_with(id=self.user_id)
            mock_queryset.exists.assert_called_once()

    def test_exists_false(self):
        """Test exists method when user doesn't exist."""
        # Arrange
        with patch.object(UserModel.objects, "filter") as mock_filter:
            mock_queryset = Mock()
            mock_filter.return_value = mock_queryset
            mock_queryset.exists.return_value = False

            # Act
            result = self.repository.exists(self.user_id)

            # Assert
            assert result is False
            mock_filter.assert_called_once_with(id=self.user_id)
            mock_queryset.exists.assert_called_once()

    def test_create_model_from_entity_with_location(self):
        """Test creating model from entity with location."""
        # Act
        result = self.repository._create_model_from_entity(self.user)

        # Assert
        assert result.id == self.user_id
        assert result.email == self.email
        assert result.name == self.name
        assert result.location_lat == float(self.location.latitude)
        assert result.location_lng == float(self.location.longitude)
        assert result.user_segments == ["new_users"]  # Default segment

    def test_create_model_from_entity_without_location(self):
        """Test creating model from entity without location."""
        # Arrange
        user_no_location = User(
            id=self.user_id,
            email=self.email,
            name=self.name,
            location=None,
            created_at="2023-01-01T00:00:00Z",
        )

        # Act
        result = self.repository._create_model_from_entity(user_no_location)

        # Assert
        assert result.id == self.user_id
        assert result.email == self.email
        assert result.name == self.name
        assert result.location_lat == 0.0
        assert result.location_lng == 0.0
        assert result.user_segments == ["new_users"]  # Default segment

    def test_update_model_from_entity_with_location_and_segments(self):
        """Test updating model from entity with location and segments."""
        # Arrange
        mock_model = Mock()

        # Act
        self.repository._update_model_from_entity(mock_model, self.user)

        # Assert
        assert mock_model.email == self.email
        assert mock_model.name == self.name
        assert mock_model.location_lat == float(self.location.latitude)
        assert mock_model.location_lng == float(self.location.longitude)
        assert mock_model.user_segments == [seg.value for seg in self.segments]

    def test_update_model_from_entity_without_location_and_segments(self):
        """Test updating model from entity without location and segments."""
        # Arrange
        mock_model = Mock()
        user_no_location = User(
            id=self.user_id,
            email=self.email,
            name=self.name,
            location=None,
            created_at="2023-01-01T00:00:00Z",
            segments=None,
        )

        # Act
        self.repository._update_model_from_entity(mock_model, user_no_location)

        # Assert
        assert mock_model.email == self.email
        assert mock_model.name == self.name
        # Location and segments should not be updated

    def test_entity_from_model_with_location(self):
        """Test creating entity from model with location."""
        # Arrange
        # Standard Python Libraries
        from datetime import datetime

        mock_model = Mock()
        mock_model.id = self.user_id
        mock_model.email = self.email
        mock_model.name = self.name
        mock_model.location_lat = float(self.location.latitude)
        mock_model.location_lng = float(self.location.longitude)
        mock_model.user_segments = [seg.value for seg in self.segments]
        mock_model.created_at = datetime(2023, 1, 1, 0, 0, 0)

        # Act
        result = self.repository._entity_from_model(mock_model)

        # Assert
        assert result.id == self.user_id
        assert result.email == self.email
        assert result.name == self.name
        assert result.location is not None
        assert (
            result.location.latitude
            == Decimal(str(mock_model.location_lat)).normalize()
        )
        assert (
            result.location.longitude
            == Decimal(str(mock_model.location_lng)).normalize()
        )
        assert result.segments == self.segments
        assert result.last_purchase_at is None
        assert result.total_purchases == 0
        assert result.total_spent == 0.0

    def test_entity_from_model_without_location(self):
        """Test creating entity from model without location."""
        # Arrange
        # Standard Python Libraries
        from datetime import datetime

        mock_model = Mock()
        mock_model.id = self.user_id
        mock_model.email = self.email
        mock_model.name = self.name
        mock_model.location_lat = None
        mock_model.location_lng = None
        mock_model.user_segments = []
        mock_model.created_at = datetime(2023, 1, 1, 0, 0, 0)

        # Act
        result = self.repository._entity_from_model(mock_model)

        # Assert
        assert result.id == self.user_id
        assert result.email == self.email
        assert result.name == self.name
        assert result.location is None
        assert result.segments == set()
        assert result.last_purchase_at is None
        assert result.total_purchases == 0
        assert result.total_spent == 0.0

    def test_entity_from_model_without_created_at(self):
        """Test creating entity from model without created_at."""
        # Arrange
        mock_model = Mock()
        mock_model.id = self.user_id
        mock_model.email = self.email
        mock_model.name = self.name
        mock_model.location_lat = None
        mock_model.location_lng = None
        mock_model.user_segments = []
        mock_model.created_at = None

        # Act
        result = self.repository._entity_from_model(mock_model)

        # Assert
        assert result.id == self.user_id
        assert result.email == self.email
        assert result.name == self.name
        assert result.location is None
        assert result.segments == set()
        # created_at will be datetime.now() due to User constructor default
        assert result.created_at is not None
        assert result.last_purchase_at is None
        assert result.total_purchases == 0
        assert result.total_spent == 0.0

    def test_get_users_by_location_empty_result(self):
        """Test getting users by location with empty result."""
        # Arrange
        with patch.object(UserModel.objects, "filter") as mock_filter:
            mock_filter.return_value = []

            # Act
            result = self.repository.get_users_by_location(self.location, 10.0)

            # Assert
            assert result == []
            mock_filter.assert_called_once()

    def test_get_users_by_segments_empty_result(self):
        """Test getting users by segments with empty result."""
        # Arrange
        segments = {UserSegment.NEW_USERS}
        with patch.object(UserModel.objects, "filter") as mock_filter:
            mock_filter.return_value = []

            # Act
            result = self.repository.get_users_by_segments(segments)

            # Assert
            assert result == []
            mock_filter.assert_called_once()

    def test_get_users_by_segments_and_location_empty_result(self):
        """Test getting users by segments and location with empty result."""
        # Arrange
        segments = {UserSegment.NEW_USERS}
        with patch.object(UserModel.objects, "filter") as mock_filter:
            mock_filter.return_value = []

            # Act
            result = self.repository.get_users_by_segments_and_location(
                segments, self.location, 10.0
            )

            # Assert
            assert result == []
            mock_filter.assert_called_once()
