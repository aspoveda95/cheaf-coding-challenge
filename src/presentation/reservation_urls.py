# Third-Party Libraries
from django.urls import path

from .views.reservation_views import (
    check_product_availability,
    get_reservation_status,
    process_purchase,
    reserve_product,
)

urlpatterns = [
    path("", reserve_product, name="reserve_product"),
    path(
        "<str:reservation_id>/status/",
        get_reservation_status,
        name="get_reservation_status",
    ),
    path("purchase/", process_purchase, name="process_purchase"),
    path(
        "product/<uuid:product_id>/availability/",
        check_product_availability,
        name="check_product_availability",
    ),
]
