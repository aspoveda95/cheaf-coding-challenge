# Standard Python Libraries
from decimal import Decimal
from uuid import UUID

# Third-Party Libraries
from rest_framework import serializers

# Local Libraries
from src.domain.value_objects.user_segment import UserSegment


class PriceSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default="USD")

    def to_representation(self, instance):
        if hasattr(instance, "amount"):
            return {"amount": str(instance.amount), "currency": "USD"}
        return super().to_representation(instance)


class TimeRangeSerializer(serializers.Serializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()


class LocationSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)


class FlashPromoCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    store_id = serializers.UUIDField()
    promo_price = PriceSerializer()
    time_range = TimeRangeSerializer()
    user_segments = serializers.ListField(
        child=serializers.ChoiceField(choices=[seg.value for seg in UserSegment])
    )
    max_radius_km = serializers.FloatField(default=2.0)

    def validate_user_segments(self, value):
        """Validate user segments."""
        valid_segments = {seg.value for seg in UserSegment}
        for segment in value:
            if segment not in valid_segments:
                raise serializers.ValidationError(f"Invalid segment: {segment}")
        return value

    def validate_time_range(self, value):
        """Validate time range."""
        if value["start_time"] >= value["end_time"]:
            raise serializers.ValidationError("Start time must be before end time")
        return value


class FlashPromoResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    product_id = serializers.UUIDField()
    store_id = serializers.UUIDField()
    promo_price = PriceSerializer()
    time_range = TimeRangeSerializer()
    user_segments = serializers.ListField(child=serializers.CharField())
    max_radius_km = serializers.FloatField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)


class FlashPromoListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    product_id = serializers.UUIDField()
    store_id = serializers.UUIDField()
    promo_price = PriceSerializer()
    time_range = TimeRangeSerializer()
    user_segments = serializers.ListField(child=serializers.CharField())
    max_radius_km = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class FlashPromoActivationSerializer(serializers.Serializer):
    promo_id = serializers.UUIDField()


class FlashPromoEligibilitySerializer(serializers.Serializer):
    promo_id = serializers.UUIDField()
    user_id = serializers.UUIDField()


class FlashPromoEligibilityResponseSerializer(serializers.Serializer):
    eligible = serializers.BooleanField()
    reason = serializers.CharField()
