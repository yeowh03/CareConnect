"""Notification Strategies for CareConnect Backend.

This module implements the Strategy pattern for notifications,
supporting multiple delivery methods including database storage,
email, and SMS notifications.
"""

from abc import ABC, abstractmethod
from ..models import Notification, db

class NotificationStrategy(ABC):
    """Abstract interface for notification strategies.
    
    Defines the contract that all notification delivery methods must implement.
    """
    
    @abstractmethod
    def create_notification(self, message: str, receiver_email: str) -> Notification:
        """Create and send notification using specific strategy.
        
        Args:
            message (str): Notification message content.
            receiver_email (str): Email of notification recipient.
            
        Returns:
            Notification: Created notification instance.
            
        Raises:
            ValueError: If required parameters are missing.
        """
        pass

class DatabaseNotificationStrategy(NotificationStrategy):
    """Database storage notification strategy.
    
    Stores notifications in the database for retrieval through the web interface.
    """
    
    def create_notification(self, message: str, receiver_email: str) -> Notification:
        if not message or not receiver_email:
            raise ValueError("message and receiver_email are required")

        notif = Notification(
            message=message,
            receiver_email=receiver_email,
        )
        db.session.add(notif)
        db.session.commit()
        return notif

class EmailNotificationStrategy(NotificationStrategy):
    """Email notification strategy.
    
    Sends notifications via email while also storing them in the database.
    """
    
    def create_notification(self, message: str, receiver_email: str) -> Notification:
        if not message or not receiver_email:
            raise ValueError("message and receiver_email are required")
        
        # Email sending logic would go here
        print(f"Sending email to {receiver_email}: {message}")
        
        # Still store in database for record keeping
        notif = Notification(
            message=message,
            receiver_email=receiver_email,
        )
        db.session.add(notif)
        db.session.commit()
        return notif

class SMSNotificationStrategy(NotificationStrategy):
    """SMS notification strategy.
    
    Sends notifications via SMS while also storing them in the database.
    """
    
    def create_notification(self, message: str, receiver_email: str) -> Notification:
        if not message or not receiver_email:
            raise ValueError("message and receiver_email are required")
        
        # SMS sending logic would go here
        print(f"Sending SMS to {receiver_email}: {message}")
        
        # Still store in database for record keeping
        notif = Notification(
            message=message,
            receiver_email=receiver_email,
        )
        db.session.add(notif)
        db.session.commit()
        return notif