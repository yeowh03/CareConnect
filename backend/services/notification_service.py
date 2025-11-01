# services/notification_service.py
from ..models import Notification, db
from .notification_strategies import (
    NotificationContext,
    DatabaseNotificationStrategy,
    BroadcastNotificationStrategy
)
from typing import List, Dict, Any


def create_notification(message: str, receiver_email: str):
    """
    Legacy function for backward compatibility.
    Uses DatabaseNotificationStrategy internally.
    """
    if not message or not receiver_email:
        raise ValueError("message and receiver_email are required")

    notif = Notification(
        message=message,
        receiver_email=receiver_email,
    )
    db.session.add(notif)
    db.session.commit()
    return notif


class NotificationService:
    """
    Enhanced notification service using strategy pattern.
    """
    
    def __init__(self):
        self.context = NotificationContext()
    
    def send_database_notification(self, message: str, recipients: List[str]) -> Dict[str, Any]:
        """Send notification via database storage"""
        self.context.set_strategy(DatabaseNotificationStrategy())
        return self.context.send_notification(message, recipients)
    
    def send_broadcast_notification(self, message: str, cc: str) -> Dict[str, Any]:
        """Send broadcast notification to CC subscribers"""
        self.context.set_strategy(BroadcastNotificationStrategy())
        return self.context.send_notification(message, [], cc=cc)
    
    def notify_low_fulfillment(self, cc: str, fulfillment_rate: float):
        """Broadcast low fulfillment rate"""
        message = f"Fulfilment rate is {fulfillment_rate:.0%}. Below target: Your donation is needed!"
        return self.send_broadcast_notification(message, cc)


notification_service = NotificationService()
