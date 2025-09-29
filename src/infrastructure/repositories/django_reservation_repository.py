"""Django ORM implementation of Reservation repository."""
# Standard Python Libraries
from datetime import datetime
from typing import List, Optional
from uuid import UUID

# Third-Party Libraries
from django.utils import timezone

# Local Libraries
from models.models import ReservationModel
from src.domain.entities.reservation import Reservation
from src.domain.repositories.reservation_repository import ReservationRepository


class DjangoReservationRepository(ReservationRepository):
    """Django ORM implementation of Reservation repository."""

    def __init__(self):
        """Initialize DjangoReservationRepository with model."""
        self._model = ReservationModel

    def save(self, reservation: Reservation) -> Reservation:
        """Save a reservation."""
        try:
            model_instance = self._model.objects.get(id=reservation.id)
            self._update_model_from_entity(model_instance, reservation)
        except self._model.DoesNotExist:
            model_instance = self._create_model_from_entity(reservation)

        model_instance.save()
        return self._entity_from_model(model_instance)

    def get_by_id(self, reservation_id: UUID) -> Optional[Reservation]:
        """Get reservation by ID."""
        try:
            model_instance = self._model.objects.get(id=reservation_id)
            return self._entity_from_model(model_instance)
        except self._model.DoesNotExist:
            return None

    def get_by_product(self, product_id: UUID) -> List[Reservation]:
        """Get reservations for a product."""
        model_instances = self._model.objects.filter(product_id=product_id)
        return [self._entity_from_model(instance) for instance in model_instances]

    def get_by_user(self, user_id: UUID) -> List[Reservation]:
        """Get reservations for a user."""
        model_instances = self._model.objects.filter(user_id=user_id)
        return [self._entity_from_model(instance) for instance in model_instances]

    def get_active_reservations(self) -> List[Reservation]:
        """Get all active (non-expired) reservations."""
        now = timezone.now()
        model_instances = self._model.objects.filter(expires_at__gt=now)
        return [self._entity_from_model(instance) for instance in model_instances]

    def get_expired_reservations(self) -> List[Reservation]:
        """Get all expired reservations."""
        now = timezone.now()
        model_instances = self._model.objects.filter(expires_at__lte=now)
        return [self._entity_from_model(instance) for instance in model_instances]

    def delete(self, reservation_id: UUID) -> bool:
        """Delete a reservation."""
        try:
            model_instance = self._model.objects.get(id=reservation_id)
            model_instance.delete()
            return True
        except self._model.DoesNotExist:
            return False

    def delete_expired(self) -> int:
        """Delete expired reservations and return count."""
        now = timezone.now()
        deleted_count, _ = self._model.objects.filter(expires_at__lte=now).delete()
        return deleted_count

    def exists_active_for_product(self, product_id: UUID) -> bool:
        """Check if there's an active reservation for a product."""
        now = timezone.now()
        return self._model.objects.filter(
            product_id=product_id, expires_at__gt=now
        ).exists()

    def _create_model_from_entity(self, reservation: Reservation) -> ReservationModel:
        """Create model instance from entity."""
        return self._model(
            id=reservation.id,
            product_id=reservation.product_id,
            user_id=reservation.user_id,
            store_id=reservation.store_id,
            flash_promo_id=reservation.flash_promo_id,
            created_at=reservation.created_at,
            expires_at=reservation.expires_at,
        )

    def _update_model_from_entity(
        self, model_instance: ReservationModel, reservation: Reservation
    ) -> None:
        """Update model instance from entity."""
        model_instance.product_id = reservation.product_id
        model_instance.user_id = reservation.user_id
        model_instance.store_id = reservation.store_id
        model_instance.flash_promo_id = reservation.flash_promo_id
        model_instance.expires_at = reservation.expires_at

    def _entity_from_model(self, model_instance: ReservationModel) -> Reservation:
        """Create entity from model instance."""
        return Reservation(
            id=model_instance.id,
            product_id=model_instance.product_id,
            user_id=model_instance.user_id,
            flash_promo_id=model_instance.flash_promo_id,
            store_id=model_instance.store_id,
            created_at=model_instance.created_at,
            expires_at=model_instance.expires_at,
        )
