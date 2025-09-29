# Third-Party Libraries
from django.urls import path

from .views.flash_promo_views import (
    activate_flash_promo,
    check_promo_eligibility,
    create_flash_promo,
    get_active_flash_promos,
    get_promo_statistics,
)

urlpatterns = [
    path("", create_flash_promo, name="create_flash_promo"),
    path("active/", get_active_flash_promos, name="get_active_flash_promos"),
    path("activate/", activate_flash_promo, name="activate_flash_promo"),
    path("eligibility/", check_promo_eligibility, name="check_promo_eligibility"),
    path(
        "<uuid:promo_id>/statistics/", get_promo_statistics, name="get_promo_statistics"
    ),
]
