# Standard Python Libraries
from unittest.mock import MagicMock, Mock
from uuid import uuid4

# Third-Party Libraries
import pytest

# Local Libraries
from src.application.services.notification_service import NotificationService
from src.application.services.promo_activation_service import PromoActivationService
from src.application.services.user_segmentation_service import UserSegmentationService
from src.application.use_cases.activate_flash_promo import ActivateFlashPromoUseCase
from src.application.use_cases.create_flash_promo import CreateFlashPromoUseCase
from src.application.use_cases.process_purchase import ProcessPurchaseUseCase
from src.application.use_cases.reserve_product import ReserveProductUseCase
from src.domain.repositories.flash_promo_repository import FlashPromoRepository
from src.domain.repositories.reservation_repository import ReservationRepository
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.adapters.cache_adapter import CacheAdapter
from src.infrastructure.container import FlashPromosContainer


class TestFlashPromosContainer:
    """Test FlashPromosContainer dependency injection."""

    def test_container_initialization(self):
        """Test container initialization."""
        container = FlashPromosContainer()

        # Verify container is created
        assert container is not None
        assert hasattr(container, "_container")

    def test_get_flash_promo_repository(self):
        """Test getting flash promo repository from container."""
        container = FlashPromosContainer()
        repo = container.get_flash_promo_repository()

        assert repo is not None
        assert isinstance(repo, FlashPromoRepository)

    def test_get_user_repository(self):
        """Test getting user repository from container."""
        container = FlashPromosContainer()
        repo = container.get_user_repository()

        assert repo is not None
        assert isinstance(repo, UserRepository)

    def test_get_reservation_repository(self):
        """Test getting reservation repository from container."""
        container = FlashPromosContainer()
        repo = container.get_reservation_repository()

        assert repo is not None
        assert isinstance(repo, ReservationRepository)

    def test_get_cache_adapter(self):
        """Test getting cache adapter from container."""
        container = FlashPromosContainer()
        adapter = container.get_cache_adapter()

        assert adapter is not None
        assert isinstance(adapter, CacheAdapter)

    def test_get_notification_service(self):
        """Test getting notification service from container."""
        container = FlashPromosContainer()
        service = container.get_notification_service()

        assert service is not None
        assert isinstance(service, NotificationService)

    def test_get_user_segmentation_service(self):
        """Test getting user segmentation service from container."""
        container = FlashPromosContainer()
        service = container.get_user_segmentation_service()

        assert service is not None
        assert isinstance(service, UserSegmentationService)

    def test_get_promo_activation_service(self):
        """Test getting promo activation service from container."""
        container = FlashPromosContainer()
        service = container.get_promo_activation_service()

        assert service is not None
        assert isinstance(service, PromoActivationService)

    def test_get_create_flash_promo_use_case(self):
        """Test getting create flash promo use case from container."""
        container = FlashPromosContainer()
        use_case = container.get_create_flash_promo_use_case()

        assert use_case is not None
        assert isinstance(use_case, CreateFlashPromoUseCase)

    def test_get_activate_flash_promo_use_case(self):
        """Test getting activate flash promo use case from container."""
        container = FlashPromosContainer()
        use_case = container.get_activate_flash_promo_use_case()

        assert use_case is not None
        assert isinstance(use_case, ActivateFlashPromoUseCase)

    def test_get_reserve_product_use_case(self):
        """Test getting reserve product use case from container."""
        container = FlashPromosContainer()
        use_case = container.get_reserve_product_use_case()

        assert use_case is not None
        assert isinstance(use_case, ReserveProductUseCase)

    def test_get_process_purchase_use_case(self):
        """Test getting process purchase use case from container."""
        container = FlashPromosContainer()
        use_case = container.get_process_purchase_use_case()

        assert use_case is not None
        assert isinstance(use_case, ProcessPurchaseUseCase)

    def test_singleton_behavior(self):
        """Test that services are singletons."""
        container = FlashPromosContainer()

        # Get same service twice
        service1 = container.get_notification_service()
        service2 = container.get_notification_service()

        # Should be the same instance
        assert service1 is service2

    def test_container_clone(self):
        """Test container cloning for testing."""
        container = FlashPromosContainer()
        cloned_container = container.clone()

        assert cloned_container is not None
        assert isinstance(cloned_container, FlashPromosContainer)
        assert cloned_container is not container

    def test_dependency_injection_chain(self):
        """Test that dependencies are properly injected."""
        container = FlashPromosContainer()

        # Get a service that depends on other services
        promo_activation_service = container.get_promo_activation_service()

        # Verify it has the required dependencies
        assert hasattr(promo_activation_service, "_flash_promo_repository")
        assert hasattr(promo_activation_service, "_user_repository")
        assert hasattr(promo_activation_service, "_notification_service")
        assert hasattr(promo_activation_service, "_user_segmentation_service")

    def test_use_case_dependencies(self):
        """Test that use cases have proper dependencies."""
        container = FlashPromosContainer()

        # Test create flash promo use case
        create_use_case = container.get_create_flash_promo_use_case()
        assert hasattr(create_use_case, "_flash_promo_repository")
        assert hasattr(create_use_case, "_user_repository")

        # Test activate flash promo use case
        activate_use_case = container.get_activate_flash_promo_use_case()
        assert hasattr(activate_use_case, "_flash_promo_repository")
        assert hasattr(activate_use_case, "_user_repository")

        # Test reserve product use case
        reserve_use_case = container.get_reserve_product_use_case()
        assert hasattr(reserve_use_case, "_flash_promo_repository")
        assert hasattr(reserve_use_case, "_reservation_repository")

        # Test process purchase use case
        purchase_use_case = container.get_process_purchase_use_case()
        assert hasattr(purchase_use_case, "_flash_promo_repository")
        assert hasattr(purchase_use_case, "_reservation_repository")
        assert hasattr(purchase_use_case, "_user_repository")

    def test_service_dependencies(self):
        """Test that services have proper dependencies."""
        container = FlashPromosContainer()

        # Test user segmentation service
        user_segmentation_service = container.get_user_segmentation_service()
        assert hasattr(user_segmentation_service, "_user_repository")

        # Test notification service
        notification_service = container.get_notification_service()
        assert hasattr(notification_service, "_channels")
        assert len(notification_service._channels) == 2  # Email and Push channels

    def test_container_protocol_compliance(self):
        """Test that container implements the protocol correctly."""
        container = FlashPromosContainer()

        # Test all protocol methods
        assert container.get_flash_promo_repository() is not None
        assert container.get_user_repository() is not None
        assert container.get_reservation_repository() is not None
        assert container.get_cache_adapter() is not None
        assert container.get_notification_service() is not None

    def test_error_handling(self):
        """Test error handling in container."""
        container = FlashPromosContainer()

        # Container should handle missing dependencies gracefully
        # This is more of an integration test, but we can verify
        # that the container doesn't crash on initialization
        assert container is not None

    def test_memory_efficiency(self):
        """Test that container doesn't create unnecessary instances."""
        container = FlashPromosContainer()

        # Get multiple services
        service1 = container.get_notification_service()
        service2 = container.get_user_segmentation_service()
        service3 = container.get_promo_activation_service()

        # All should be created without errors
        assert service1 is not None
        assert service2 is not None
        assert service3 is not None

        # Get same service again - should be same instance
        service1_again = container.get_notification_service()
        assert service1 is service1_again
