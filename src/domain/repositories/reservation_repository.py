"""Reservation repository interface."""
# Standard Python Libraries
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

# Local Libraries
from src.domain.entities.reservation import Reservation


class ReservationRepository(ABC):
    """Abstract repository for Reservation entities."""

    @abstractmethod
    def save(self, reservation: Reservation) -> Reservation:
        """Save a reservation."""
        pass

    @abstractmethod
    def get_by_id(self, reservation_id: UUID) -> Optional[Reservation]:
        """Get reservation by ID."""
        pass

    @abstractmethod
    def get_by_product(self, product_id: UUID) -> List[Reservation]:
        """Get reservations for a product."""
        pass

    @abstractmethod
    def get_by_user(self, user_id: UUID) -> List[Reservation]:
        """Get reservations for a user."""
        pass

    @abstractmethod
    def get_active_reservations(self) -> List[Reservation]:
        """Get all active (non-expired) reservations."""
        pass

    @abstractmethod
    def get_expired_reservations(self) -> List[Reservation]:
        """Get all expired reservations."""
        pass

    @abstractmethod
    def delete(self, reservation_id: UUID) -> bool:
        """Delete a reservation."""
        pass

    @abstractmethod
    def delete_expired(self) -> int:
        """Delete expired reservations and return count."""
        pass

    @abstractmethod
    def exists_active_for_product(self, product_id: UUID) -> bool:
        """Check if there's an active reservation for a product."""
        pass
