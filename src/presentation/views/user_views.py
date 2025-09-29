# Standard Python Libraries
from decimal import Decimal
from uuid import UUID

# Third-Party Libraries
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Local Libraries
from src.application.services.user_segmentation_service import UserSegmentationService
from src.domain.entities.user import User
from src.domain.value_objects.location import Location
from src.domain.value_objects.user_segment import UserSegment
from src.infrastructure.repositories.django_user_repository import DjangoUserRepository
from src.presentation.serializers.user_serializer import (
    UserCreateSerializer,
    UserResponseSerializer,
    UserSegmentationResponseSerializer,
    UserSegmentSerializer,
    UserStatisticsSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def create_user(request):
    """Create a new user."""
    serializer = UserCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Initialize dependencies
        user_repo = DjangoUserRepository()

        # Extract data
        data = serializer.validated_data
        email = data["email"]
        name = data["name"]
        location_data = data.get("location")

        # Create location if provided
        location = None
        if location_data:
            location = Location(
                Decimal(str(location_data["latitude"])),
                Decimal(str(location_data["longitude"])),
            )

        # Create user
        user = User(email=email, name=name, location=location)

        # Save user
        saved_user = user_repo.save(user)

        # Serialize response
        response_data = {
            "id": saved_user.id,
            "email": saved_user.email,
            "name": saved_user.name,
            "location": {
                "latitude": str(saved_user.location.latitude.normalize()),
                "longitude": str(saved_user.location.longitude.normalize()),
            }
            if saved_user.location
            else None,
            "created_at": saved_user.created_at,
            "last_purchase_at": saved_user.last_purchase_at,
            "total_purchases": saved_user.total_purchases,
            "total_spent": saved_user.total_spent,
            "segments": [seg.value for seg in saved_user.segments],
        }

        response_serializer = UserResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        # Standard Python Libraries
        import traceback

        print(f"Error in create_user: {str(e)}")
        print(traceback.format_exc())
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_user(request, user_id):
    """Get user by ID."""
    try:
        # Initialize dependencies
        user_repo = DjangoUserRepository()

        # Get user
        user_uuid = user_id if isinstance(user_id, UUID) else UUID(user_id)
        user = user_repo.get_by_id(user_uuid)

        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Serialize response
        response_data = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "location": {
                "latitude": str(user.location.latitude),
                "longitude": str(user.location.longitude),
            }
            if user.location
            else None,
            "created_at": user.created_at,
            "last_purchase_at": user.last_purchase_at,
            "total_purchases": user.total_purchases,
            "total_spent": user.total_spent,
            "segments": [seg.value for seg in user.segments],
        }

        response_serializer = UserResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    except ValueError:  # noqa: F841
        return Response(
            {"error": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def update_user_segments(request, user_id):
    """Update user segments."""
    serializer = UserSegmentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Initialize dependencies
        user_repo = DjangoUserRepository()

        # Get user
        user_uuid = user_id if isinstance(user_id, UUID) else UUID(user_id)
        user = user_repo.get_by_id(user_uuid)

        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Update segments
        segments_data = serializer.validated_data["segments"]
        user_segments = {UserSegment(seg) for seg in segments_data}

        # Add new segments (don't clear existing ones)
        for segment in user_segments:
            user.add_segment(segment)

        # Save user directly
        updated_user = user_repo.save(user)

        # Serialize response
        response_data = {
            "user_id": updated_user.id,
            "segments": [seg.value for seg in updated_user.segments],
            "is_new_user": updated_user.is_new_user(),
            "is_frequent_buyer": updated_user.is_frequent_buyer(),
            "is_vip_customer": updated_user.is_vip_customer(),
        }

        response_serializer = UserSegmentationResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    except ValueError:  # noqa: F841
        return Response(
            {"error": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_user_statistics(request):
    """Get user segmentation statistics."""
    try:
        # Initialize dependencies
        user_repo = DjangoUserRepository()
        user_segmentation_service = UserSegmentationService(user_repo)

        # Get all users
        all_users = user_repo.get_users_by_segments(set(UserSegment))

        # Get statistics
        stats = user_segmentation_service.get_segment_statistics(all_users)

        # Serialize response
        response_serializer = UserStatisticsSerializer(stats)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
