# Third-Party Libraries
from django.urls import path

from .views.user_views import (
    create_user,
    get_user,
    get_user_statistics,
    update_user_segments,
)

urlpatterns = [
    path("", create_user, name="create_user"),
    path("<uuid:user_id>/", get_user, name="get_user"),
    path("<uuid:user_id>/segments/", update_user_segments, name="update_user_segments"),
    path("statistics/", get_user_statistics, name="get_user_statistics"),
]
