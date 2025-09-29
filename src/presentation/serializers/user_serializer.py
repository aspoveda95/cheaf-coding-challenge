# Standard Python Libraries
from uuid import UUID

# Third-Party Libraries
from rest_framework import serializers

# Local Libraries
from src.domain.value_objects.user_segment import UserSegment


class LocationSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(max_length=255)
    location = LocationSerializer(required=False)


class UserResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField()
    name = serializers.CharField()
    location = LocationSerializer(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    last_purchase_at = serializers.DateTimeField(required=False)
    total_purchases = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2)
    segments = serializers.ListField(child=serializers.CharField(), read_only=True)


class UserSegmentSerializer(serializers.Serializer):
    segments = serializers.ListField(
        child=serializers.ChoiceField(choices=[seg.value for seg in UserSegment])
    )

    def validate_segments(self, value):
        """Validate user segments."""
        valid_segments = {seg.value for seg in UserSegment}
        for segment in value:
            if segment not in valid_segments:
                raise serializers.ValidationError(f"Invalid segment: {segment}")
        return value


class UserSegmentationResponseSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    segments = serializers.ListField(child=serializers.CharField())
    is_new_user = serializers.BooleanField()
    is_frequent_buyer = serializers.BooleanField()
    is_vip_customer = serializers.BooleanField()


class UserStatisticsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    new_users = serializers.IntegerField()
    frequent_buyers = serializers.IntegerField()
    vip_customers = serializers.IntegerField()
    users_with_location = serializers.IntegerField()
