"""Notification Routes for CareConnect Backend.

This module defines Flask routes for notification management including
broadcast subscriptions, notification CRUD, and Observer pattern endpoints.
"""

from flask import Blueprint
from ..controllers.notification_controller import NotificationController as c

notification_bp = Blueprint("notifications", __name__, url_prefix="/api")

# Subscribe to CC broadcast notifications (Observer pattern)
@notification_bp.route("/broadcast/subscribe", methods=["POST"])
def subscribe_broadcast():
    return c.subscribe_broadcast()

# Unsubscribe from CC broadcast notifications
@notification_bp.route("/broadcast/unsubscribe", methods=["POST"])
def unsubscribe_broadcast():
    return c.unsubscribe_broadcast()

# List user's current broadcast subscriptions
@notification_bp.route("/broadcast/subscriptions", methods=["GET"])
def list_subscriptions():
    return c.list_subscriptions()

# Get user's notifications (latest 50)
@notification_bp.route("/notifications", methods=["GET"])
def my_notifications():
    return c.my_notifications()

# Delete specific notification
@notification_bp.route("/notifications/<int:notification_id>", methods=["DELETE"])
def delete_notification(notification_id: int):
    return c.delete_notification(notification_id)

# Get count of unread notifications
@notification_bp.route("/notifications/unread-count", methods=["GET"])
def get_unread_count():
    return c.get_unread_count()

# Mark all notifications as read
@notification_bp.route("/notifications/mark-read", methods=["POST"])
def mark_all_read():
    return c.mark_all_read()

