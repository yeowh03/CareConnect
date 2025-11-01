# backend/examples/controller_notification_usage.py
"""
Example of how controllers can use notification strategies.
"""

from ..services.notification_service import notification_service
from ..services.notification_strategies import NotificationContext, DatabaseNotificationStrategy, BroadcastNotificationStrategy


class EnhancedDonationController:
    """Example of donation controller using notification strategies"""
    
    @staticmethod
    def manager_approve_with_strategy(donation_id: int):
        """Approve donation using notification strategy"""
        # ... existing approval logic ...
        
        # Use database notification strategy
        notification_service.send_database_notification(
            f"Your donation has been approved by the manager. Please deliver within 2 days.",
            ["donor@example.com"]
        )
        
        return {"ok": True, "notification_sent": True}
    
    @staticmethod
    def manager_add_with_broadcast(donation_id: int):
        """Add donation and broadcast to community"""
        # ... existing add logic ...
        
        # Use broadcast strategy for community update
        notification_service.send_broadcast_notification(
            "New items added to inventory! Check available donations.",
            "CC1"
        )
        
        return {"ok": True, "broadcast_sent": True}


class EnhancedAllocationService:
    """Example of allocation service using notification strategies"""
    
    @staticmethod
    def run_allocation_with_notifications():
        """Run allocation and send appropriate notifications"""
        # ... existing allocation logic ...
        
        # Notify matched users via database
        matched_users = ["user1@example.com", "user2@example.com"]
        notification_service.send_database_notification(
            "Your request has been matched! Please collect your items.",
            matched_users
        )
        
        # Check fulfillment rate and broadcast if low
        fulfillment_rate = 0.3  # Example low rate
        if fulfillment_rate < 0.5:
            notification_service.notify_low_fulfillment("CC1", fulfillment_rate)
        
        return {"allocation_complete": True, "notifications_sent": True}


class EnhancedProfileController:
    """Example of profile controller using notification strategies"""
    
    @staticmethod
    def process_registration_with_strategy(outcome: bool, email: str):
        """Process registration using notification strategies"""
        context = NotificationContext()
        
        if outcome:
            # Approved - use database strategy
            context.set_strategy(DatabaseNotificationStrategy())
            context.send_notification(
                "Your registration has been approved. Welcome to CareConnect!",
                [email]
            )
        else:
            # Rejected - use database strategy with different message
            context.set_strategy(DatabaseNotificationStrategy())
            context.send_notification(
                "Your registration has been rejected. Please contact support for more information.",
                [email]
            )
        
        return {"ok": True, "notification_strategy": "database"}