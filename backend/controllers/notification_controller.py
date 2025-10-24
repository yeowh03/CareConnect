from flask import jsonify, request
from ..models import Notification, db  # keep db import if you later need it
from ..services.find_user import get_current_user
from ..services.broadcast_observer import subject, SubscriptionObserver


class NotificationController:
    """Encapsulates all notification-related request handling."""

    @staticmethod
    def create_notification(message, receiver_email):
        """
        Create a new notification record in the database.
        Parameters:
            message (str): The message content.
            receiver_email (str): The email of the receiver.
        """
        if not message or not receiver_email:
            return {"error": "message and receiver_email are required"}, 400

        try:
            new_notification = Notification(
                message=message,
                receiver_email=receiver_email,
                is_read=False
            )
            db.session.add(new_notification)
            db.session.commit()
            return {"ok": True, "id": new_notification.id}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    # POST /api/broadcast/subscribe
    @staticmethod
    def subscribe_broadcast():
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
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        } for n in rows]

        return jsonify({"notifications": data}), 200
