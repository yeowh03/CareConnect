# backend/examples/notification_strategy_usage.py
"""
Example usage of notification strategies in CareConnect.
"""

from ..services.notification_strategies import (
    NotificationContext,
    DatabaseNotificationStrategy,
    BroadcastNotificationStrategy,
    EmailNotificationStrategy,
    MultiChannelNotificationStrategy
)
from ..services.notification_service import notification_service


class NotificationExamples:
    """Examples of notification strategy usage"""
    
    @staticmethod
    def database_notification_example():
        """Send individual database notification"""
        context = NotificationContext()
        context.set_strategy(DatabaseNotificationStrategy())
        
        result = context.send_notification(
            "Your donation has been approved!",
            ["user@example.com"]
        )
        return result
    
    @staticmethod
    def broadcast_notification_example():
        """Send broadcast notification to community center"""
        context = NotificationContext()
        context.set_strategy(BroadcastNotificationStrategy())
        
        result = context.send_notification(
            "Urgent: Low donation levels detected!",
            [],
            cc="CC1"
        )
        return result
    
    @staticmethod
    def multi_channel_notification_example():
        """Send notification through multiple channels"""
        strategies = [
            DatabaseNotificationStrategy(),
            BroadcastNotificationStrategy()
        ]
        
        context = NotificationContext()
        context.set_strategy(MultiChannelNotificationStrategy(strategies))
        
        result = context.send_notification(
            "System maintenance scheduled",
            ["admin@example.com"],
            cc="CC1"
        )
        return result
    
    @staticmethod
    def service_layer_examples():
        """Examples using the NotificationService"""
        
        # Database notification
        db_result = notification_service.send_database_notification(
            "Welcome to CareConnect!",
            ["newuser@example.com"]
        )
        
        # Broadcast notification
        broadcast_result = notification_service.send_broadcast_notification(
            "Donations needed urgently!",
            "CC1"
        )
        
        # Low fulfillment notification
        fulfillment_result = notification_service.notify_low_fulfillment("CC1", 0.3)
        
        return {
            "database": db_result,
            "broadcast": broadcast_result,
            "fulfillment": fulfillment_result
        }