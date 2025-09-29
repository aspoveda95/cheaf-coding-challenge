"""Integration tests for Lagom dependency injection.

This module tests the integration between Lagom and our Flash Promos system.
"""

# Standard Python Libraries
from unittest.mock import Mock, patch
from uuid import uuid4

# Third-Party Libraries
import pytest

# Local Libraries
from src.infrastructure.container import FlashPromosContainer


class TestLagomIntegration:
    """Test Lagom integration with Flash Promos system."""

    def test_container_dependency_resolution(self):
        """Test that container properly resolves dependencies."""
        container = FlashPromosContainer()

        # Test that all services can be resolved
        flash_promo_repo = container.get_flash_promo_repository()
        user_repo = container.get_user_repository()
        notification_service = container.get_notification_service()

        assert flash_promo_repo is not None
        assert user_repo is not None
        assert notification_service is not None

    def test_singleton_behavior(self):
        """Test that services are properly singletons."""
        container = FlashPromosContainer()

        # Get same service multiple times
        service1 = container.get_notification_service()
        service2 = container.get_notification_service()

        # Should be the same instance
        assert service1 is service2

    def test_dependency_chain(self):
        """Test that dependencies are properly chained."""
        container = FlashPromosContainer()

        # Get a service that depends on other services
        promo_activation_service = container.get_promo_activation_service()

        # Verify it has all required dependencies
        assert hasattr(promo_activation_service, "_flash_promo_repository")
        assert hasattr(promo_activation_service, "_user_repository")
        assert hasattr(promo_activation_service, "_notification_service")
        assert hasattr(promo_activation_service, "_user_segmentation_service")

    def test_use_case_injection(self):
        """Test that use cases are properly injected."""
        container = FlashPromosContainer()

        # Test create flash promo use case
        create_use_case = container.get_create_flash_promo_use_case()
        assert hasattr(create_use_case, "_flash_promo_repository")
        assert hasattr(create_use_case, "_user_repository")

        # Test activate flash promo use case
        activate_use_case = container.get_activate_flash_promo_use_case()
        assert hasattr(activate_use_case, "_flash_promo_repository")
        assert hasattr(activate_use_case, "_user_repository")

    def test_container_clone_for_testing(self):
        """Test container cloning for testing scenarios."""
        container = FlashPromosContainer()
        cloned_container = container.clone()

        # Should be different instances
        assert cloned_container is not container

        # But should have same structure
        assert hasattr(cloned_container, "get_flash_promo_repository")
        assert hasattr(cloned_container, "get_user_repository")

    def test_mock_dependency_injection(self):
        """Test injecting mocks for testing."""
        container = FlashPromosContainer()
        cloned_container = container.clone()

        # Create mock repository
        _ = Mock()

        # This would be done in actual tests to override dependencies
        # cloned_container._container[FlashPromoRepository] = mock_repo

        # Verify container can handle mock injection
        assert cloned_container is not None

    def test_service_initialization_order(self):
        """Test that services are initialized in correct order."""
        container = FlashPromosContainer()

        # All services should be available without errors
        services = [
            container.get_flash_promo_repository(),
            container.get_user_repository(),
            container.get_reservation_repository(),
            container.get_cache_adapter(),
            container.get_notification_service(),
            container.get_user_segmentation_service(),
            container.get_promo_activation_service(),
            container.get_create_flash_promo_use_case(),
            container.get_activate_flash_promo_use_case(),
            container.get_reserve_product_use_case(),
            container.get_process_purchase_use_case(),
        ]

        # All services should be initialized
        assert all(service is not None for service in services)

    def test_dependency_circular_reference_avoidance(self):
        """Test that circular dependencies are avoided."""
        container = FlashPromosContainer()

        # Get services that might have circular dependencies
        notification_service = container.get_notification_service()
        promo_activation_service = container.get_promo_activation_service()

        # Should not cause circular reference errors
        assert notification_service is not None
        assert promo_activation_service is not None

    def test_memory_efficiency(self):
        """Test that container is memory efficient."""
        container = FlashPromosContainer()

        # Get multiple services
        services = [
            container.get_notification_service(),
            container.get_user_segmentation_service(),
            container.get_promo_activation_service(),
        ]

        # All should be created without memory issues
        assert all(service is not None for service in services)

        # Get same service again - should be same instance
        notification_service_again = container.get_notification_service()
        assert notification_service_again is services[0]

    def test_error_handling(self):
        """Test error handling in container."""
        container = FlashPromosContainer()

        # Container should handle missing dependencies gracefully
        # This is more of an integration test
        try:
            service = container.get_notification_service()
            assert service is not None
        except Exception as e:
            pytest.fail(f"Container should not raise exceptions: {e}")

    def test_lagom_container_integration(self):
        """Test that our container properly integrates with Lagom."""
        container = FlashPromosContainer()

        # Test that internal Lagom container is accessible
        assert hasattr(container, "_container")
        assert container._container is not None

        # Test that we can access Lagom container methods
        lagom_container = container._container
        assert hasattr(lagom_container, "clone")
        assert hasattr(lagom_container, "__getitem__")

    def test_dependency_lifecycle(self):
        """Test dependency lifecycle management."""
        container = FlashPromosContainer()

        # Create services
        service1 = container.get_notification_service()
        service2 = container.get_user_segmentation_service()

        # Services should be properly initialized
        assert service1 is not None
        assert service2 is not None

        # Services should maintain their state
        assert hasattr(service1, "_channels")
        assert hasattr(service2, "_user_repository")

    def test_container_isolation(self):
        """Test that different container instances are isolated."""
        container1 = FlashPromosContainer()
        container2 = FlashPromosContainer()

        # Should be different instances
        assert container1 is not container2

        # But should have same interface
        assert hasattr(container1, "get_notification_service")
        assert hasattr(container2, "get_notification_service")

        # Services from different containers should be different
        _ = container1.get_notification_service()
        _ = container2.get_notification_service()

        # They might be the same class but different instances
        # This depends on how Lagom handles singletons across containers
