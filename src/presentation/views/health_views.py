# Third-Party Libraries
from django.core.cache import cache
from django.db import connection
import redis
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    # Check cache connection
    try:
        cache.set("health_check", "ok", 10)
        cache_status = "healthy" if cache.get("health_check") == "ok" else "unhealthy"
    except Exception:
        cache_status = "unhealthy"

    # Check Redis connection
    try:
        redis_client = redis.from_url("redis://redis:6379/0")
        redis_client.ping()
        redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"

    overall_status = (
        "healthy"
        if all(
            [
                db_status == "healthy",
                cache_status == "healthy",
                redis_status == "healthy",
            ]
        )
        else "unhealthy"
    )

    return Response(
        {
            "status": overall_status,
            "services": {
                "database": db_status,
                "cache": cache_status,
                "redis": redis_status,
            },
        },
        status=status.HTTP_200_OK
        if overall_status == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE,
    )
