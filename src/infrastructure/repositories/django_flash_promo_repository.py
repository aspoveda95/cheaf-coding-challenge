"""Django ORM implementation of Flash Promo repository."""
# Standard Python Libraries
from typing import List, Optional, Set
from uuid import UUID

# Third-Party Libraries
from django.utils import timezone

# Local Libraries
from models.models import FlashPromoModel
from src.domain.entities.flash_promo import FlashPromo
from src.domain.repositories.flash_promo_repository import FlashPromoRepository
from src.domain.value_objects.user_segment import UserSegment


class DjangoFlashPromoRepository(FlashPromoRepository):
    """Django ORM implementation of Flash Promo repository."""

    def __init__(self):
        """Initialize DjangoFlashPromoRepository with model."""
        self._model = FlashPromoModel

    def save(self, flash_promo: FlashPromo) -> FlashPromo:
        """Save a flash promo."""
        try:
            model_instance = self._model.objects.get(id=flash_promo.id)
            self._update_model_from_entity(model_instance, flash_promo)
        except self._model.DoesNotExist:
            model_instance = self._create_model_from_entity(flash_promo)

        model_instance.save()
        return self._entity_from_model(model_instance)

    def get_by_id(self, promo_id: UUID) -> Optional[FlashPromo]:
        """Get flash promo by ID."""
        try:
            model_instance = self._model.objects.get(id=promo_id)
            return self._entity_from_model(model_instance)
        except self._model.DoesNotExist:
            return None

    def get_active_promos(self) -> List[FlashPromo]:
        """Get all active flash promos."""
        model_instances = self._model.objects.filter(is_active=True)
        return [self._entity_from_model(instance) for instance in model_instances]

    def get_promos_by_product(self, product_id: UUID) -> List[FlashPromo]:
        """Get flash promos for a specific product."""
        model_instances = self._model.objects.filter(product_id=product_id)
        return [self._entity_from_model(instance) for instance in model_instances]

    def get_promos_by_store(self, store_id: UUID) -> List[FlashPromo]:
        """Get flash promos for a specific store."""
        model_instances = self._model.objects.filter(store_id=store_id)
        return [self._entity_from_model(instance) for instance in model_instances]

    def get_promos_by_segments(self, segments: Set[UserSegment]) -> List[FlashPromo]:
        """Get flash promos for specific user segments."""
        segment_values = [seg.value for seg in segments]
        model_instances = self._model.objects.filter(
            user_segments__overlap=segment_values
        )
        return [self._entity_from_model(instance) for instance in model_instances]

    def delete(self, promo_id: UUID) -> bool:
        """Delete a flash promo."""
        try:
            model_instance = self._model.objects.get(id=promo_id)
            model_instance.delete()
            return True
        except self._model.DoesNotExist:
            return False

    def exists(self, promo_id: UUID) -> bool:
        """Check if flash promo exists."""
        return self._model.objects.filter(id=promo_id).exists()

    def _create_model_from_entity(self, flash_promo: FlashPromo) -> FlashPromoModel:
        """Create model instance from entity."""
        # Local Libraries
        from src.domain.value_objects.price import Price
        from src.domain.value_objects.time_range import TimeRange

        return self._model(
            id=flash_promo.id,
            product_id=flash_promo.product_id,
            store_id=flash_promo.store_id,
            promo_price_amount=flash_promo.promo_price.amount
            if flash_promo.promo_price
            else 0,
            start_time=flash_promo.time_range.start_time
            if flash_promo.time_range
            else None,
            end_time=flash_promo.time_range.end_time
            if flash_promo.time_range
            else None,
            user_segments=[seg.value for seg in flash_promo.user_segments],
            max_radius_km=flash_promo.max_radius_km,
            is_active=flash_promo.is_active,
            created_at=flash_promo.created_at,
        )

    def _update_model_from_entity(
        self, model_instance: FlashPromoModel, flash_promo: FlashPromo
    ) -> None:
        """Update model instance from entity."""
        # Local Libraries
        from src.domain.value_objects.price import Price
        from src.domain.value_objects.time_range import TimeRange

        model_instance.product_id = flash_promo.product_id
        model_instance.store_id = flash_promo.store_id
        model_instance.promo_price_amount = (
            flash_promo.promo_price.amount if flash_promo.promo_price else 0
        )
        model_instance.start_time = (
            flash_promo.time_range.start_time if flash_promo.time_range else None
        )
        model_instance.end_time = (
            flash_promo.time_range.end_time if flash_promo.time_range else None
        )
        model_instance.user_segments = [seg.value for seg in flash_promo.user_segments]
        model_instance.max_radius_km = flash_promo.max_radius_km
        model_instance.is_active = flash_promo.is_active

    def _entity_from_model(self, model_instance: FlashPromoModel) -> FlashPromo:
        """Create entity from model instance."""
        # Local Libraries
        from src.domain.value_objects.price import Price
        from src.domain.value_objects.time_range import TimeRange

        promo_price = (
            Price(model_instance.promo_price_amount)
            if model_instance.promo_price_amount
            else None
        )

        time_range = None
        if model_instance.start_time and model_instance.end_time:
            time_range = TimeRange(model_instance.start_time, model_instance.end_time)

        user_segments = {UserSegment(seg) for seg in model_instance.user_segments}

        # Handle created_at safely
        created_at = model_instance.created_at
        if (
            created_at
            and hasattr(created_at, "replace")
            and created_at.tzinfo is not None
        ):
            created_at = created_at.replace(tzinfo=None)

        return FlashPromo(
            id=model_instance.id,
            product_id=model_instance.product_id,
            store_id=model_instance.store_id,
            promo_price=promo_price,
            time_range=time_range,
            user_segments=user_segments,
            max_radius_km=model_instance.max_radius_km,
            is_active=model_instance.is_active,
            created_at=created_at,
        )
