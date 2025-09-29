"""Django ORM implementation of User repository."""
# Standard Python Libraries
from decimal import Decimal
import math
from typing import List, Optional, Set
from uuid import UUID

# Third-Party Libraries
from geopy.distance import geodesic

# Local Libraries
from models.models import UserModel
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.location import Location
from src.domain.value_objects.user_segment import UserSegment

# No GIS dependencies needed - using lat/lng only


class DjangoUserRepository(UserRepository):
    """Django ORM implementation of User repository."""

    def __init__(self):
        """Initialize DjangoUserRepository with model."""
        self._model = UserModel

    def _calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points using Haversine formula."""
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # Radius of earth in kilometers
        r = 6371
        return c * r

    def save(self, user: User) -> User:
        """Save a user."""
        try:
            model_instance = self._model.objects.get(id=user.id)
            self._update_model_from_entity(model_instance, user)
        except self._model.DoesNotExist:
            model_instance = self._create_model_from_entity(user)

        try:
            model_instance.save()
        except Exception as e:
            print(f"Error saving user model: {str(e)}")
            # Standard Python Libraries
            import traceback

            traceback.print_exc()
            raise
        return self._entity_from_model(model_instance)

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        try:
            model_instance = self._model.objects.get(id=user_id)
            return self._entity_from_model(model_instance)
        except self._model.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            model_instance = self._model.objects.get(email=email)
            return self._entity_from_model(model_instance)
        except self._model.DoesNotExist:
            return None

    def get_users_by_segments(self, segments: Set[UserSegment]) -> List[User]:
        """Get users by segments."""
        segment_values = [seg.value for seg in segments]
        model_instances = self._model.objects.filter(
            user_segments__overlap=segment_values
        )
        return [self._entity_from_model(instance) for instance in model_instances]

    def get_users_by_location(self, location: Location, radius_km: float) -> List[User]:
        """Get users within radius of location using optimized GeoPy method."""
        if not location:
            return []

        # Use optimized method with bounding box
        return self._get_users_within_radius_optimized(location, radius_km)

    def _get_users_within_radius_optimized(
        self, location: Location, radius_km: float
    ) -> List[User]:
        """Optimized method using bounding box + GeoPy geodesic distance."""
        center_lat = float(location.latitude)
        center_lng = float(location.longitude)

        # Create bounding box for initial filtering (much faster than full scan)
        # Approximate conversion: 1 degree ≈ 111.32 km
        lat_range = radius_km / 111.32
        lng_range = radius_km / (111.32 * math.cos(math.radians(center_lat)))

        # Filter users within bounding box first (database-level filtering)
        candidates = self._model.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            latitude__range=(center_lat - lat_range, center_lat + lat_range),
            longitude__range=(center_lng - lng_range, center_lng + lng_range),
        )

        # Now calculate precise distance only for candidates
        nearby_users = []
        center_point = (center_lat, center_lng)

        for user_model in candidates:
            user_point = (float(user_model.latitude), float(user_model.longitude))

            # Use GeoPy geodesic for precise distance calculation
            distance_km = geodesic(center_point, user_point).kilometers

            if distance_km <= radius_km:
                nearby_users.append(self._entity_from_model(user_model))

        return nearby_users

    def get_users_by_segments_and_location(
        self, segments: Set[UserSegment], location: Location, radius_km: float
    ) -> List[User]:
        """Get users by segments and location using optimized method."""
        segment_values = [seg.value for seg in segments]

        if not location:
            # No location filtering, just segment filtering
            model_instances = self._model.objects.filter(
                user_segments__overlap=segment_values
            )
            return [self._entity_from_model(instance) for instance in model_instances]

        # Use optimized method with bounding box + GeoPy
        return self._get_users_by_segments_and_location_optimized(
            segments, location, radius_km
        )

    def _get_users_by_segments_and_location_optimized(
        self, segments: Set[UserSegment], location: Location, radius_km: float
    ) -> List[User]:
        """Optimized method for segments + location filtering."""
        segment_values = [seg.value for seg in segments]
        center_lat = float(location.latitude)
        center_lng = float(location.longitude)

        # Create bounding box for initial filtering
        lat_range = radius_km / 111.32
        lng_range = radius_km / (111.32 * math.cos(math.radians(center_lat)))

        # Filter by segments AND bounding box at database level
        candidates = self._model.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            latitude__range=(center_lat - lat_range, center_lat + lat_range),
            longitude__range=(center_lng - lng_range, center_lng + lng_range),
            user_segments__overlap=segment_values,  # Filter by segments at DB level
        )

        # Calculate precise distance only for candidates
        nearby_users = []
        center_point = (center_lat, center_lng)

        for user_model in candidates:
            user_point = (float(user_model.latitude), float(user_model.longitude))

            # Use GeoPy geodesic for precise distance calculation
            distance_km = geodesic(center_point, user_point).kilometers

            if distance_km <= radius_km:
                nearby_users.append(self._entity_from_model(user_model))

        return nearby_users

    def delete(self, user_id: UUID) -> bool:
        """Delete a user."""
        try:
            model_instance = self._model.objects.get(id=user_id)
            model_instance.delete()
            return True
        except self._model.DoesNotExist:
            return False

    def exists(self, user_id: UUID) -> bool:
        """Check if user exists."""
        return self._model.objects.filter(id=user_id).exists()

    def _create_model_from_entity(self, user: User) -> UserModel:
        """Create model instance from entity."""
        return self._model(
            id=user.id,
            email=user.email,
            name=user.name,
            location_lat=float(user.location.latitude) if user.location else 0.0,
            location_lng=float(user.location.longitude) if user.location else 0.0,
            user_segments=["new_users"],  # Default segment
        )

    def _update_model_from_entity(self, model_instance: UserModel, user: User) -> None:
        """Update model instance from entity."""
        model_instance.email = user.email
        model_instance.name = user.name

        if user.location:
            model_instance.location_lat = float(user.location.latitude)
            model_instance.location_lng = float(user.location.longitude)

        # Update segments if user has segments
        if user.segments:
            model_instance.user_segments = [seg.value for seg in user.segments]

        # Don't update created_at and updated_at - let Django handle them

    def _entity_from_model(self, model_instance: UserModel) -> User:
        """Create entity from model instance."""
        location = None
        if model_instance.location_lat and model_instance.location_lng:
            location = Location(
                Decimal(str(model_instance.location_lat)).normalize(),
                Decimal(str(model_instance.location_lng)).normalize(),
            )

        user_segments = {UserSegment(seg) for seg in model_instance.user_segments}

        # Handle created_at safely
        created_at = model_instance.created_at
        if (
            created_at
            and hasattr(created_at, "replace")
            and created_at.tzinfo is not None
        ):
            created_at = created_at.replace(tzinfo=None)

        return User(
            id=model_instance.id,
            email=model_instance.email,
            name=model_instance.name,
            location=location,
            created_at=created_at,
            last_purchase_at=None,  # Not stored in model
            total_purchases=0,  # Not stored in model
            total_spent=0.0,  # Not stored in model
            segments=user_segments,
        )
