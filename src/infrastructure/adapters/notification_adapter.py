"""Celery notification adapter for bulk notifications."""
# Standard Python Libraries
from typing import List, Optional
from uuid import UUID

# Third-Party Libraries
from celery import Celery
from django.conf import settings

# Local Libraries
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.user import User


class CeleryNotificationAdapter:
    """Celery adapter for sending bulk notifications."""

    def __init__(self):
        """Initialize CeleryNotificationAdapter with Celery app."""
        self._celery_app = Celery("flash_promos")
        self._celery_app.config_from_object("django.conf:settings", namespace="CELERY")

    def send_bulk_notifications(
        self, users: List[User], promo: FlashPromo, batch_size: int = 1000
    ) -> str:
        """Send bulk notifications using Celery.

        Args:
            users: List of users to notify
            promo: Flash promo to notify about
            batch_size: Size of each batch

        Returns:
            Task ID for tracking
        """
        user_batches = self._create_user_batches(users, batch_size)

        task = self._celery_app.send_task(
            "notifications.send_bulk_notifications",
            args=[user_batches, str(promo.id)],
            queue="notifications",
        )

        return task.id

    def send_immediate_notification(
        self, user: User, promo: FlashPromo, message: Optional[str] = None
    ) -> str:
        """Send immediate notification to a single user.

        Args:
            user: User to notify
            promo: Flash promo to notify about
            message: Custom message

        Returns:
            Task ID for tracking
        """
        task = self._celery_app.send_task(
            "notifications.send_immediate_notification",
            args=[str(user.id), str(promo.id), message],
            queue="notifications_high_priority",
        )

        return task.id

    def schedule_notification(
        self, users: List[User], promo: FlashPromo, eta: str
    ) -> str:
        """Schedule notification for a specific time.

        Args:
            users: List of users to notify
            promo: Flash promo to notify about
            eta: When to send the notification (ISO format)

        Returns:
            Task ID for tracking
        """
        task = self._celery_app.send_task(
            "notifications.schedule_notification",
            args=[[str(u.id) for u in users], str(promo.id)],
            eta=eta,
            queue="notifications_scheduled",
        )

        return task.id

    def _create_user_batches(
        self, users: List[User], batch_size: int
    ) -> List[List[str]]:
        """Create batches of user IDs."""
        user_ids = [str(user.id) for user in users]
        batches = []

        for i in range(0, len(user_ids), batch_size):
            batch = user_ids[i : i + batch_size]
            batches.append(batch)

        return batches

    def get_task_status(self, task_id: str) -> dict:
        """Get status of a notification task."""
        try:
            result = self._celery_app.AsyncResult(task_id)
            return {
                "task_id": task_id,
                "status": result.status,
                "result": result.result if result.ready() else None,
                "ready": result.ready(),
            }
        except Exception as e:
            return {
                "task_id": task_id,
                "status": "ERROR",
                "error": str(e),
                "ready": True,
            }
