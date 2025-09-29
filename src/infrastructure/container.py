"""Dependency Injection Container using Lagom.

This module provides a centralized container for managing dependencies
in the Flash Promos system using the Lagom dependency injection framework.
"""

# Standard Python Libraries
from typing import Protocol

# Third-Party Libraries
from lagom import Container, Singleton

# Local Libraries
from src.application.services.notification_service import (
    EmailNotificationChannel,
    NotificationService,
    PushNotificationChannel,
)
from src.application.services.promo_activation_service import PromoActivationService
from src.application.services.user_segmentation_service import UserSegmentationService
from src.application.use_cases.activate_flash_promo import ActivateFlashPromoUseCase
from src.application.use_cases.create_flash_promo import CreateFlashPromoUseCase
from src.application.use_cases.process_purchase import ProcessPurchaseUseCase
from src.application.use_cases.reserve_product import ReserveProductUseCase
from src.domain.repositories.flash_promo_repository import FlashPromoRepository
from src.domain.repositories.reservation_repository import ReservationRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.services.email_service import EmailService
from src.domain.services.push_notification_service import PushNotificationService
from src.domain.services.sms_service import SMSService
from src.infrastructure.adapters.cache_adapter import CacheAdapter
from src.infrastructure.adapters.notification_adapter import CeleryNotificationAdapter
from src.infrastructure.repositories.django_flash_promo_repository import (
    DjangoFlashPromoRepository,
)
from src.infrastructure.repositories.django_reservation_repository import (
    DjangoReservationRepository,
)
from src.infrastructure.repositories.django_user_repository import DjangoUserRepository
from src.infrastructure.services.mock_email_service import MockEmailService
from src.infrastructure.services.mock_push_notification_service import (
    MockPushNotificationService,
)
from src.infrastructure.services.mock_sms_service import MockSMSService


class ContainerProtocol(Protocol):
    """Protocol for dependency injection container."""

    def get_flash_promo_repository(self) -> FlashPromoRepository:
        """Get flash promo repository."""
        ...

    def get_user_repository(self) -> UserRepository:
        """Get user repository."""
        ...

    def get_reservation_repository(self) -> ReservationRepository:
        """Get reservation repository."""
        ...

    def get_cache_adapter(self) -> CacheAdapter:
        """Get cache adapter."""
        ...

    def get_notification_service(self) -> NotificationService:
        """Get notification service."""
        ...


class FlashPromosContainer:
    """Dependency injection container for Flash Promos system.

    This container manages all dependencies using Lagom, providing
    a clean separation between domain, application, and infrastructure layers.
    """

    def __init__(self):
        """Initialize the container and setup dependencies."""
        self._container = Container()
        self._setup_dependencies()

    def _setup_dependencies(self):
        """Setup all dependencies in the container."""
        # Infrastructure Layer - Repositories
        self._container[FlashPromoRepository] = Singleton(DjangoFlashPromoRepository)
        self._container[UserRepository] = Singleton(DjangoUserRepository)
        self._container[ReservationRepository] = Singleton(DjangoReservationRepository)

        # Infrastructure Layer - Adapters
        self._container[CacheAdapter] = Singleton(CacheAdapter)
        self._container[CeleryNotificationAdapter] = Singleton(
            CeleryNotificationAdapter
        )

        # Application Layer - Services
        self._container[UserSegmentationService] = Singleton(
            lambda c: UserSegmentationService(c[UserRepository])
        )

        # Notification Service with channels
        self._container[NotificationService] = Singleton(
            lambda c: NotificationService(
                [
                    EmailNotificationChannel(),
                    PushNotificationChannel(),
                ]
            )
        )

        # Infrastructure Layer - Notification Services (Mock implementations)
        self._container[EmailService] = Singleton(MockEmailService)
        self._container[PushNotificationService] = Singleton(
            MockPushNotificationService
        )
        self._container[SMSService] = Singleton(MockSMSService)

        # Promo activation service
        self._container[PromoActivationService] = Singleton(
            lambda c: PromoActivationService(
                c[FlashPromoRepository],
                c[UserRepository],
                c[EmailService],
                c[PushNotificationService],
                c[SMSService],
                c[UserSegmentationService],
                c[NotificationService],
            )
        )

        # Application Layer - Use Cases
        self._container[CreateFlashPromoUseCase] = Singleton(
            lambda c: CreateFlashPromoUseCase(
                c[FlashPromoRepository], c[UserRepository]
            )
        )

        self._container[ActivateFlashPromoUseCase] = Singleton(
            lambda c: ActivateFlashPromoUseCase(
                c[FlashPromoRepository], c[UserRepository]
            )
        )

        self._container[ReserveProductUseCase] = Singleton(
            lambda c: ReserveProductUseCase(
                c[FlashPromoRepository], c[ReservationRepository]
            )
        )

        self._container[ProcessPurchaseUseCase] = Singleton(
            lambda c: ProcessPurchaseUseCase(
                c[FlashPromoRepository], c[ReservationRepository], c[UserRepository]
            )
        )

    def get_flash_promo_repository(self) -> FlashPromoRepository:
        """Get flash promo repository."""
        return self._container[FlashPromoRepository]

    def get_user_repository(self) -> UserRepository:
        """Get user repository."""
        return self._container[UserRepository]

    def get_reservation_repository(self) -> ReservationRepository:
        """Get reservation repository."""
        return self._container[ReservationRepository]

    def get_cache_adapter(self) -> CacheAdapter:
        """Get cache adapter."""
        return self._container[CacheAdapter]

    def get_notification_service(self) -> NotificationService:
        """Get notification service."""
        return self._container[NotificationService]

    def get_user_segmentation_service(self) -> UserSegmentationService:
        """Get user segmentation service."""
        return self._container[UserSegmentationService]

    def get_promo_activation_service(self) -> PromoActivationService:
        """Get promo activation service."""
        return self._container[PromoActivationService]

    def get_create_flash_promo_use_case(self) -> CreateFlashPromoUseCase:
        """Get create flash promo use case."""
        return self._container[CreateFlashPromoUseCase]

    def get_activate_flash_promo_use_case(self) -> ActivateFlashPromoUseCase:
        """Get activate flash promo use case."""
        return self._container[ActivateFlashPromoUseCase]

    def get_reserve_product_use_case(self) -> ReserveProductUseCase:
        """Get reserve product use case."""
        return self._container[ReserveProductUseCase]

    def get_process_purchase_use_case(self) -> ProcessPurchaseUseCase:
        """Get process purchase use case."""
        return self._container[ProcessPurchaseUseCase]

    def clone(self) -> "FlashPromosContainer":
        """Clone the container for testing."""
        new_container = FlashPromosContainer()
        new_container._container = self._container.clone()
        return new_container


# Global container instance
container = FlashPromosContainer()
