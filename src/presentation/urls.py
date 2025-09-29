# Third-Party Libraries
from django.urls import include, path

urlpatterns = [
    path(
        "flash-promos/",
        include(
            [
                path("", include("src.presentation.flash_promo_urls")),
            ]
        ),
    ),
    path(
        "reservations/",
        include(
            [
                path("", include("src.presentation.reservation_urls")),
            ]
        ),
    ),
    path(
        "users/",
        include(
            [
                path("", include("src.presentation.user_urls")),
            ]
        ),
    ),
]
