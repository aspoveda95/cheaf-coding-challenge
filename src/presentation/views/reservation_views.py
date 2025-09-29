# Standard Python Libraries
from datetime import datetime, timedelta
from uuid import UUID

# Third-Party Libraries
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Local Libraries
# Note: Use cases are now obtained from the container
from src.presentation.serializers.reservation_serializer import (
    PurchaseResponseSerializer,
    PurchaseSerializer,
    ReservationCreateSerializer,
    ReservationResponseSerializer,
    ReservationStatusResponseSerializer,
    ReservationStatusSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def reserve_product(request):
    """Reserve a product for a user during a flash promo."""
    serializer = ReservationCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Get use case from container (lazy import)
        # Local Libraries
        from src.infrastructure.container import container

        reserve_use_case = container.get_reserve_product_use_case()

        # Extract data
        data = serializer.validated_data
        product_id = data["product_id"]
        user_id = data["user_id"]
        flash_promo_id = data["flash_promo_id"]
        reservation_duration_minutes = data["reservation_duration_minutes"]

        # Reserve product
        reservation = reserve_use_case.execute(
            product_id=product_id,
            user_id=user_id,
            flash_promo_id=flash_promo_id,
            reservation_duration_minutes=reservation_duration_minutes,
        )

        if not reservation:
            return Response(
                {"error": "Product is already reserved or promo is not active"},
                status=status.HTTP_409_CONFLICT,
            )

        # Serialize response
        response_data = {
            "id": str(reservation.id) if reservation.id else None,
            "product_id": str(reservation.product_id)
            if reservation.product_id
            else None,
            "user_id": str(reservation.user_id) if reservation.user_id else None,
            "flash_promo_id": str(reservation.flash_promo_id)
            if reservation.flash_promo_id
            else None,
            "created_at": reservation.created_at,
            "expires_at": reservation.expires_at,
            "time_remaining_seconds": reservation.time_remaining_seconds(),
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_reservation_status(request, reservation_id):
    """Get status of a reservation."""
    try:
        # Convert string to UUID and validate
        try:
            reservation_uuid = UUID(reservation_id)
        except ValueError:
            return Response(
                {"error": "Invalid reservation ID format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get use case from container (lazy import)
        # Local Libraries
        from src.infrastructure.container import container

        reserve_use_case = container.get_reserve_product_use_case()

        # Get reservation
        reservation = reserve_use_case.get_reservation(reservation_uuid)

        if not reservation:
            return Response(
                {"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Serialize response
        response_data = {
            "id": str(reservation.id) if reservation.id else None,
            "is_expired": reservation.is_expired(),
            "time_remaining_seconds": reservation.time_remaining_seconds(),
            "expires_at": reservation.expires_at,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ValueError:  # noqa: F841
        return Response(
            {"error": "Invalid reservation ID"}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def process_purchase(request):
    """Process a purchase for a reserved product."""
    serializer = PurchaseSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Get use case from container (lazy import)
        # Local Libraries
        from src.infrastructure.container import container

        purchase_use_case = container.get_process_purchase_use_case()

        # Extract data
        data = serializer.validated_data
        reservation_id = data["reservation_id"]
        user_id = data["user_id"]

        # Process purchase
        success = purchase_use_case.execute(reservation_id, user_id)

        if not success:
            return Response(
                {"error": "Purchase could not be processed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get purchase price
        purchase_price = purchase_use_case.get_purchase_price(reservation_id)

        # Serialize response
        response_data = {
            "success": True,
            "message": "Purchase completed successfully",
            "purchase_price": float(purchase_price.amount) if purchase_price else None,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ValueError as e:
        print(f"ValueError in process_purchase: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def check_product_availability(request, product_id):
    """Check if a product is available for reservation."""
    try:
        # Get use case from container (lazy import)
        # Local Libraries
        from src.infrastructure.container import container

        reserve_use_case = container.get_reserve_product_use_case()

        # Check availability
        product_uuid = product_id if isinstance(product_id, UUID) else UUID(product_id)
        is_reserved = reserve_use_case.is_product_reserved(product_uuid)

        return Response(
            {
                "product_id": str(product_id)
                if hasattr(product_id, "__str__")
                else product_id,
                "is_available": not is_reserved,
                "is_reserved": is_reserved,
            },
            status=status.HTTP_200_OK,
        )

    except ValueError:  # noqa: F841
        return Response(
            {"error": "Invalid product ID"}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
