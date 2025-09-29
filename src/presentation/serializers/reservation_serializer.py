# Standard Python Libraries
from uuid import UUID

# Third-Party Libraries
from rest_framework import serializers


class ReservationCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    flash_promo_id = serializers.UUIDField()
    reservation_duration_minutes = serializers.IntegerField(
        default=1, min_value=1, max_value=60
    )


class ReservationResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    product_id = serializers.UUIDField(read_only=True)
    user_id = serializers.UUIDField(read_only=True)
    flash_promo_id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)
    time_remaining_seconds = serializers.IntegerField(read_only=True)


class ReservationStatusSerializer(serializers.Serializer):
    reservation_id = serializers.UUIDField()


class ReservationStatusResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    is_expired = serializers.BooleanField()
    time_remaining_seconds = serializers.IntegerField()
    expires_at = serializers.DateTimeField()


class PurchaseSerializer(serializers.Serializer):
    reservation_id = serializers.UUIDField()
    user_id = serializers.UUIDField()


class PurchaseResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    purchase_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
