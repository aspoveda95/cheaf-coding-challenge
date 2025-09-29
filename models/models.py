"""Django models for the Flash Promos system."""

# Standard Python Libraries
from uuid import uuid4 as UUID

# Third-Party Libraries
from django.db import models


class FlashPromoModel(models.Model):
    """Django model for Flash Promo entity."""

    id = models.UUIDField(primary_key=True, default=UUID)
    product_id = models.UUIDField()
    store_id = models.UUIDField()
    promo_price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    promo_price_currency = models.CharField(max_length=3, default="USD")
    start_time = models.TimeField()
    end_time = models.TimeField()
    user_segments = models.JSONField(default=list)
    max_radius_km = models.FloatField(default=2.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "flash_promos"
        verbose_name = "Flash Promo"
        verbose_name_plural = "Flash Promos"

    def __str__(self):
        return f"Flash Promo {self.id}"


class UserModel(models.Model):
    """Django model for User entity."""

    id = models.UUIDField(primary_key=True, default=UUID)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    location_lat = models.FloatField()
    location_lng = models.FloatField()
    user_segments = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"User {self.email}"


class ReservationModel(models.Model):
    """Django model for Reservation entity."""

    id = models.UUIDField(primary_key=True, default=UUID)
    user_id = models.UUIDField()
    product_id = models.UUIDField()
    store_id = models.UUIDField()
    flash_promo_id = models.UUIDField(null=True, blank=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reservations"
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"

    def __str__(self):
        return f"Reservation {self.id}"
