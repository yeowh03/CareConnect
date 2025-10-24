# services/notification_service.py
from ..models import Notification, db

def create_notification(message: str, receiver_email: str):
    """
    Pure service function: creates and commits a notification.
    Returns the Notification instance for convenience.
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
