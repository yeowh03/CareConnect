"""Notification Service for CareConnect Backend.

This module provides notification functionality using the Strategy pattern.
Currently implements database-based notifications with support for future
notification methods like email, SMS, or push notifications.
"""

from .notification_strategies import DatabaseNotificationStrategy

# Create default strategy instance
db_strategy = DatabaseNotificationStrategy()

def create_notification(message: str, receiver_email: str):
    """Create a notification for a user.
    
    Legacy function for backward compatibility.
    Uses DatabaseNotificationStrategy internally.
    
    Args:
        message (str): The notification message content.
        receiver_email (str): Email address of the notification recipient.
        
    Returns:
        The result of the notification creation operation.
    """
    return db_strategy.create_notification(message, receiver_email)

