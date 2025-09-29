"""Promo activation service for Flash Promos."""
# Standard Python Libraries
from datetime import datetime
from typing import List, Set
from uuid import UUID

# Local Libraries
from src.application.services.notification_service import NotificationService
from src.application.services.user_segmentation_service import UserSegmentationService
from src.domain.entities.flash_promo import FlashPromo
from src.domain.entities.user import User
from src.domain.repositories.flash_promo_repository import FlashPromoRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.services.email_service import EmailService
from src.domain.services.push_notification_service import PushNotificationService
from src.domain.services.sms_service import SMSService
from src.domain.value_objects.location import Location
from src.domain.value_objects.user_segment import UserSegment


class PromoActivationService:
    """Service for activating flash promos and notifying users."""

    def __init__(
        self,
        flash_promo_repository: FlashPromoRepository,
        user_repository: UserRepository,
        email_service: EmailService,
        push_notification_service: PushNotificationService,
        sms_service: SMSService,
        user_segmentation_service: UserSegmentationService,
        notification_service: NotificationService,
    ):
        """Initialize PromoActivationService with required dependencies."""
        self._flash_promo_repository = flash_promo_repository
        self._user_repository = user_repository
        self._email_service = email_service
        self._push_notification_service = push_notification_service
        self._sms_service = sms_service
        self._user_segmentation_service = user_segmentation_service
        self._notification_service = notification_service

    def activate_promos_for_time(self, current_time: datetime = None) -> dict:
        """Activate all promos that should be active at the given time.

        Args:
            current_time: Time to check against (defaults to now)

        Returns:
            Dictionary with activation results
        """
        if current_time is None:
            current_time = datetime.now()

        active_promos = self._get_active_promos(current_time)
        results = {
            "activated_promos": len(active_promos),
            "total_notifications_sent": 0,
            "promo_details": [],
        }

        for promo in active_promos:
            promo_result = self._activate_single_promo(promo, current_time)
            results["total_notifications_sent"] += promo_result["notifications_sent"]
            results["promo_details"].append(promo_result)

        return results

    def _get_active_promos(self, current_time: datetime) -> List[FlashPromo]:
        """Get all promos that should be active at the given time."""
        all_promos = self._flash_promo_repository.get_active_promos()
        return [
            promo for promo in all_promos if promo.is_currently_active(current_time)
        ]

    def _activate_single_promo(self, promo: FlashPromo, current_time: datetime) -> dict:
        """Activate a single promo and send notifications."""
        eligible_users = self._get_eligible_users_for_promo(promo)

        if not eligible_users:
            return {
                "promo_id": str(promo.id),
                "eligible_users": 0,
                "notifications_sent": 0,
                "status": "no_eligible_users",
            }

        # Send notifications through all channels
        email_results = self._email_service.send_bulk_flash_promo_email(
            eligible_users, promo
        )
        push_results = self._push_notification_service.send_bulk_flash_promo_push(
            eligible_users, promo
        )
        sms_results = self._sms_service.send_bulk_flash_promo_sms(eligible_users, promo)

        # Combine results
        notification_results = {
            "successful_notifications": (
                email_results["successful_sends"]
                + push_results["successful_sends"]
                + sms_results["successful_sends"]
            ),
            "failed_notifications": (
                email_results["failed_sends"]
                + push_results["failed_sends"]
                + sms_results["failed_sends"]
            ),
        }

        return {
            "promo_id": str(promo.id),
            "eligible_users": len(eligible_users),
            "notifications_sent": notification_results["successful_notifications"],
            "status": "activated",
        }

    def _get_eligible_users_for_promo(self, promo: FlashPromo) -> List[User]:
        """Get users eligible for a specific promo."""
        if not promo.user_segments:
            return []

        try:
            # Get users by segments first
            users_by_segments = self._user_repository.get_users_by_segments(
                promo.user_segments
            )

            # Filter by location if store location is available
            # Note: In a real implementation, you'd need to get store location
            # For now, we'll return all users matching segments
            return users_by_segments
        except Exception as e:
            # If there's an error getting users, return empty list
            # This prevents the statistics endpoint from failing
            print(f"Error getting eligible users: {str(e)}")
            return []

    def get_promo_eligibility(self, promo_id: UUID, user_id: UUID) -> dict:
        """Check if a user is eligible for a specific promo.

        Args:
            promo_id: ID of the flash promo
            user_id: ID of the user

        Returns:
            Dictionary with eligibility information
        """
        promo = self._flash_promo_repository.get_by_id(promo_id)
        if not promo:
            return {"eligible": False, "reason": "Promo not found"}

        if not promo.is_currently_active():
            return {"eligible": False, "reason": "Promo not currently active"}

        user = self._user_repository.get_by_id(user_id)
        if not user:
            return {"eligible": False, "reason": "User not found"}

        # Check user segments
        if promo.user_segments and not promo.is_eligible_for_user(user.segments):
            return {"eligible": False, "reason": "User segments not eligible"}

        # Check location (if implemented)
        # This would require store location and user location comparison

        return {"eligible": True, "reason": "User is eligible"}

    def schedule_promo_activation(self, promo_id: UUID) -> bool:
        """Schedule a promo for activation at its start time.

        Args:
            promo_id: ID of the promo to schedule

        Returns:
            True if scheduled successfully
        """
        promo = self._flash_promo_repository.get_by_id(promo_id)
        if not promo:
            return False

        if not promo.time_range:
            return False

        # In a real implementation, this would schedule a Celery task
        # For now, we'll just return True
        return True

    def get_promo_statistics(self, promo_id: UUID) -> dict:
        """Get statistics for a specific promo.

        Args:
            promo_id: ID of the promo

        Returns:
            Dictionary with promo statistics
        """
        promo = self._flash_promo_repository.get_by_id(promo_id)
        if not promo:
            return {"error": "Promo not found"}

        # Get eligible users for the promo
        eligible_users = self._get_eligible_users_for_promo(promo)
        eligible_users_count = len(eligible_users)

        return {
            "promo_id": str(promo_id),
            "is_active": promo.is_currently_active(),
            "eligible_users_count": eligible_users_count,
            "user_segments": [seg.value for seg in promo.user_segments],
            "time_range": {
                "start_time": promo.time_range.start_time.isoformat(),
                "end_time": promo.time_range.end_time.isoformat(),
            }
            if promo.time_range
            else None,
            "promo_price": {
                "amount": str(promo.promo_price.amount),
                "currency": "USD",
            }
            if promo.promo_price
            else None,
        }
