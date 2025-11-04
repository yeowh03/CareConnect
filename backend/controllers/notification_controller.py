"""Notification Controller for CareConnect Backend.

This module handles notification operations including creation, deletion,
broadcast subscriptions using the Observer pattern, and notification management.
"""

from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func
from ..models import Notification, db  # keep db import if you later need it
from ..services.find_user import get_current_user
from ..broadcast_observer import subject, SubscriptionObserver
from ..services.notification_strategies import DatabaseNotificationStrategy

class NotificationController:
    """Controller for notification and broadcast operations.
    
    Handles notification CRUD operations and broadcast subscription management
    using the Observer pattern for community club notifications.
    """
    def __init__(self):
        self.notification_strategy = DatabaseNotificationStrategy()
    
    @staticmethod
    def create_notification(message, receiver_email, link=None):
        """Create a new notification.
        
        Args:
            message (str): Notification message content.
            receiver_email (str): Email of notification recipient.
            link (str, optional): Optional link for notification.
            
        Returns:
            tuple: Response dict and HTTP status code.
        """
        strategy = DatabaseNotificationStrategy()
        try:
            notif = strategy.create_notification(message, receiver_email)
            return {"ok": True, "id": notif.id}, 201
        except ValueError as ve:
            return {"error": str(ve)}, 400
        except Exception as e:
            # Note: the service already committed/raised, but keep this guard.
            return {"error": str(e)}, 500
        
    @staticmethod
    def delete_notification(notification_id: int):
        """Delete a notification owned by current user.
        
        Args:
            notification_id (int): ID of notification to delete.
            
        Returns:
            tuple: JSON response and HTTP status code.
        """
        user = get_current_user()
        if not user:
            return jsonify({"message": "Unauthorized"}), 401

        n = Notification.query.filter_by(id=notification_id, receiver_email=user.email).first()
        if not n:
            return jsonify({"message": "Notification not found"}), 404

        try:
            db.session.delete(n)
            db.session.commit()
            return jsonify({"ok": True, "id": notification_id}), 200
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({"message": "Database constraint violation while deleting notification", "error": str(e)}), 409
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"message": "Database error while deleting notification", "error": str(e)}), 500
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Unexpected error while deleting notification", "error": str(e)}), 500

    # POST /api/broadcast/subscribe
    @staticmethod
    def subscribe_broadcast():
        """Subscribe to community club broadcasts.
        
        Returns:
            tuple: JSON response and HTTP status code.
        """
        user = get_current_user()
        if not user:
            return jsonify({"message": "Unauthorized"}), 401

        data = request.get_json(force=True, silent=True) or {}
        cc = (data.get("cc") or "").strip()
        if not cc:
            return jsonify({"message": "cc is required"}), 400

        # In-memory subscription (Observer pattern)
        if not subject.find(user.email, cc):
            subject.register(
                SubscriptionObserver(user_email=user.email, cc=cc, _subject=subject)
            )

        return jsonify({"ok": True, "cc": cc, "subscribed": True}), 200

    # POST /api/broadcast/unsubscribe
    @staticmethod
    def unsubscribe_broadcast():
        """Unsubscribe from community club broadcasts.
        
        Returns:
            tuple: JSON response and HTTP status code.
        """
        user = get_current_user()
        if not user:
            return jsonify({"message": "Unauthorized"}), 401

        data = request.get_json(force=True, silent=True) or {}
        cc = (data.get("cc") or "").strip()
        if not cc:
            return jsonify({"message": "cc is required"}), 400

        obs = subject.find(user.email, cc)
        if obs:
            subject.unregister(obs)

        return jsonify({"ok": True, "cc": cc, "subscribed": False}), 200

    # GET /api/broadcast/subscriptions
    @staticmethod
    def list_subscriptions():
        """List user's broadcast subscriptions.
        
        Returns:
            tuple: JSON response with subscriptions and HTTP status code.
        """
        user = get_current_user()
        if not user:
            return jsonify({"message": "Unauthorized"}), 401

        subs = subject.subscriptions_for_user(user.email)
        # Simple shape for frontend
        data = [{"cc": s.cc, "active": True, "id": f"{s.user_email}-{s.cc}"} for s in subs]
        return jsonify({"subscriptions": data}), 200

    # GET /api/notifications
    @staticmethod
    def my_notifications():
        """Get user's notifications.
        
        Returns:
            tuple: JSON response with notifications and HTTP status code.
        """
        user = get_current_user()
        if not user:
            return jsonify({"message": "Unauthorized"}), 401

        rows = (
            Notification.query
            .filter_by(receiver_email=user.email)
            .order_by(Notification.created_at.desc())
            .limit(50)
            .all()
        )
        data = [{
            "id": n.id,
            "message": n.message,
            "created_at": n.created_at.isoformat(),
        } for n in rows]

        return jsonify({"notifications": data}), 200

    @staticmethod
    def get_unread_count():
        """Get unread notification count.
        
        Return the number of unread notifications for the current user.
        Does NOT mark them as read.
        
        Returns:
            tuple: JSON response with unread count and HTTP status code.
        """
        user = get_current_user()
        if not user:
            return jsonify({"message": "Unauthorized"}), 401

        try:
            unread_count = (
                db.session.query(func.count(Notification.id))
                .filter_by(receiver_email=user.email, viewed=False)
                .scalar()
            )
            return jsonify({"unread": int(unread_count)}), 200
        except SQLAlchemyError as e:
            return jsonify({"message": "Database error while fetching unread count", "error": str(e)}), 500
        except Exception as e:
            return jsonify({"message": "Unexpected error while fetching unread count", "error": str(e)}), 500

    @staticmethod
    def mark_all_read():
        """Mark all notifications as read.
        
        Mark all notifications as read for the current user.
        
        Returns:
            tuple: JSON response and HTTP status code.
        """
        user = get_current_user()
        if not user:
            return jsonify({"message": "Unauthorized"}), 401

        try:
            Notification.query.filter_by(
                receiver_email=user.email, viewed=False
            ).update({"viewed": True})
            db.session.commit()
            return jsonify({"message": "Marked all as read"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to mark read", "error": str(e)}), 500
