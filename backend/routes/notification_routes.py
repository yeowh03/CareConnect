# Thin routing layer that wires HTTP paths to controller methods.

from flask import Blueprint
from ..controllers.notification_controller import NotificationController as c

notification_bp = Blueprint("notifications", __name__, url_prefix="/api")

# --- Broadcast subscription routes ---
@notification_bp.route("/broadcast/subscribe", methods=["POST"])
def subscribe_broadcast():
    return c.subscribe_broadcast()

@notification_bp.route("/broadcast/unsubscribe", methods=["POST"])
def unsubscribe_broadcast():
    return c.unsubscribe_broadcast()

@notification_bp.route("/broadcast/subscriptions", methods=["GET"])
def list_subscriptions():
    return c.list_subscriptions()

# --- Notifications for current user ---
@notification_bp.route("/notifications", methods=["GET"])
def my_notifications():
    return c.my_notifications()
