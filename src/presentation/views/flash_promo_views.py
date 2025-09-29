# Standard Python Libraries
from datetime import datetime, time
from decimal import Decimal
from typing import Set
from uuid import UUID

# Third-Party Libraries
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Local Libraries
from src.application.services import (
    EmailNotificationChannel,
    NotificationService,
    PromoActivationService,
    PushNotificationChannel,
    UserSegmentationService,
)
from src.application.use_cases import ActivateFlashPromoUseCase, CreateFlashPromoUseCase
from src.domain.value_objects import Price, TimeRange, UserSegment
from src.infrastructure.adapters import CacheAdapter

# from src.infrastructure.container import container  # Lazy import to avoid Django setup issues
from src.infrastructure.repositories import (
    DjangoFlashPromoRepository,
    DjangoUserRepository,
)
from src.presentation.serializers.flash_promo_serializer import (
    FlashPromoActivationSerializer,
    FlashPromoCreateSerializer,
    FlashPromoEligibilityResponseSerializer,
    FlashPromoEligibilitySerializer,
    FlashPromoListSerializer,
    FlashPromoResponseSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def create_flash_promo(request):
    """Create a new flash promo."""
    serializer = FlashPromoCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Get use case from container (lazy import)
        # Local Libraries
        from src.infrastructure.container import container

        create_use_case = container.get_create_flash_promo_use_case()

        # Extract data
        data = serializer.validated_data
        product_id = (
            data["product_id"]
            if isinstance(data["product_id"], UUID)
            else UUID(data["product_id"])
        )
        store_id = (
            data["store_id"]
            if isinstance(data["store_id"], UUID)
            else UUID(data["store_id"])
        )

        promo_price = Price(data["promo_price"]["amount"])

        # Handle time parsing - check if already time objects or strings
        start_time = data["time_range"]["start_time"]
        end_time = data["time_range"]["end_time"]

        if isinstance(start_time, time):
            start_time_obj = start_time
        else:
            start_time_obj = time.fromisoformat(start_time)

        if isinstance(end_time, time):
            end_time_obj = end_time
        else:
            end_time_obj = time.fromisoformat(end_time)

        time_range = TimeRange(start_time_obj, end_time_obj)

        user_segments = {UserSegment(seg) for seg in data["user_segments"]}
        max_radius_km = data["max_radius_km"]

        # Create flash promo
        flash_promo = create_use_case.execute(
            product_id=product_id,
            store_id=store_id,
            promo_price=promo_price,
            time_range=time_range,
            user_segments=user_segments,
            max_radius_km=max_radius_km,
        )

        # Return simple response first
        return Response(
            {
                "id": str(flash_promo.id),
                "product_id": str(flash_promo.product_id),
                "store_id": str(flash_promo.store_id),
                "promo_price": {
                    "amount": str(flash_promo.promo_price.amount),
                    "currency": "USD",
                },
                "time_range": {
                    "start_time": flash_promo.time_range.start_time.strftime(
                        "%H:%M:%S"
                    ),
                    "end_time": flash_promo.time_range.end_time.strftime("%H:%M:%S"),
                },
                "user_segments": [seg.value for seg in flash_promo.user_segments],
                "max_radius_km": flash_promo.max_radius_km,
                "is_active": flash_promo.is_active,
                "created_at": flash_promo.created_at.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        # Standard Python Libraries
        import traceback

        print(f"Error in create_flash_promo: {str(e)}")
        print(traceback.format_exc())
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_active_flash_promos(request):
    """Get all currently active flash promos."""
    try:
        # Initialize dependencies
        flash_promo_repo = DjangoFlashPromoRepository()
        user_repo = DjangoUserRepository()

        # Create use case
        activate_use_case = ActivateFlashPromoUseCase(flash_promo_repo, user_repo)

        # Get active promos
        active_promos = activate_use_case.get_active_promos()

        # Serialize response
        promos_data = []
        for promo in active_promos:
            promo_data = {
                "id": str(promo.id),
                "product_id": str(promo.product_id),
                "store_id": str(promo.store_id),
                "promo_price": {
                    "amount": str(promo.promo_price.amount),
                    "currency": "USD",
                },
                "time_range": {
                    "start_time": promo.time_range.start_time.isoformat(),
                    "end_time": promo.time_range.end_time.isoformat(),
                },
                "user_segments": [seg.value for seg in promo.user_segments],
                "max_radius_km": f"{promo.max_radius_km:.2f}",
                "is_active": promo.is_active,
                "created_at": promo.created_at,
            }
            promos_data.append(promo_data)

        return Response(promos_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def activate_flash_promo(request):
    """Activate a flash promo."""
    serializer = FlashPromoActivationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Get use case from container (lazy import)
        # Local Libraries
        from src.infrastructure.container import container

        activate_use_case = container.get_activate_flash_promo_use_case()

        # Activate promo
        promo_id = serializer.validated_data["promo_id"]
        if not isinstance(promo_id, UUID):
            promo_id = UUID(promo_id)
        activated_promo = activate_use_case.execute(promo_id)

        return Response(
            {
                "message": "Flash promo activated successfully",
                "promo_id": str(activated_promo.id),
            },
            status=status.HTTP_200_OK,
        )

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def check_promo_eligibility(request):
    """Check if a user is eligible for a flash promo."""
    serializer = FlashPromoEligibilitySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Get service from container (lazy import)
        # Local Libraries
        from src.infrastructure.container import container

        promo_activation_service = container.get_promo_activation_service()

        # Check eligibility
        promo_id = serializer.validated_data["promo_id"]
        if not isinstance(promo_id, UUID):
            promo_id = UUID(promo_id)
        user_id = serializer.validated_data["user_id"]
        if not isinstance(user_id, UUID):
            user_id = UUID(user_id)

        eligibility_result = promo_activation_service.get_promo_eligibility(
            promo_id, user_id
        )

        # Serialize response
        response_serializer = FlashPromoEligibilityResponseSerializer(
            eligibility_result
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # Standard Python Libraries
        import traceback

        print(f"Error in check_promo_eligibility: {str(e)}")
        print(traceback.format_exc())
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_promo_statistics(request, promo_id):
    """Get statistics for a specific flash promo."""
    try:
        # Get service from container (lazy import)
        # Local Libraries
        from src.infrastructure.container import container

        promo_activation_service = container.get_promo_activation_service()

        # Get statistics
        stats = promo_activation_service.get_promo_statistics(promo_id)

        return Response(stats, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
