"""Flash Promo repository interface."""
# Standard Python Libraries
from abc import ABC, abstractmethod
from typing import List, Optional, Set
from uuid import UUID

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.value_objects.user_segment import UserSegment


class FlashPromoRepository(ABC):
    """Abstract repository for Flash Promo entities."""

    @abstractmethod
    def save(self, flash_promo: FlashPromo) -> FlashPromo:
        """Save a flash promo."""
        pass

    @abstractmethod
    def get_by_id(self, promo_id: UUID) -> Optional[FlashPromo]:
        """Get flash promo by ID."""
        pass

    @abstractmethod
    def get_active_promos(self) -> List[FlashPromo]:
        """Get all active flash promos."""
        pass

    @abstractmethod
    def get_promos_by_product(self, product_id: UUID) -> List[FlashPromo]:
        """Get flash promos for a specific product."""
        pass

    @abstractmethod
    def get_promos_by_store(self, store_id: UUID) -> List[FlashPromo]:
        """Get flash promos for a specific store."""
        pass

    @abstractmethod
    def get_promos_by_segments(self, segments: Set[UserSegment]) -> List[FlashPromo]:
        """Get flash promos for specific user segments."""
        pass

    @abstractmethod
    def delete(self, promo_id: UUID) -> bool:
        """Delete a flash promo."""
        pass

    @abstractmethod
    def exists(self, promo_id: UUID) -> bool:
        """Check if flash promo exists."""
        pass
