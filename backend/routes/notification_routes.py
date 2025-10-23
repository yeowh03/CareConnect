# from flask import Blueprint, jsonify, request
# from ..extensions import db
# from ..models import BroadcastSubscription, Notification
# from ..services.find_user import get_current_user
# from ..services.metrics import check_and_broadcast_for_cc

# broadcast_bp = Blueprint("broadcasts", __name__, url_prefix="/api")

# @broadcast_bp.route("/broadcast/subscribe", methods=["POST"])
# def subscribe_broadcast():
#     u = get_current_user()
#     if not u:
#         return jsonify({"message": "Unauthorized"}), 401
#     data = request.get_json(force=True, silent=True) or {}
#     cc = (data.get("cc") or "").strip()
#     if not cc:
#         return jsonify({"message": "cc is required"}), 400
#     sub = BroadcastSubscription.query.filter_by(email=u.email, cc=cc).first()
#     if not sub:
#         sub = BroadcastSubscription(email=u.email, cc=cc)
#         db.session.add(sub)
#     db.session.commit()

#     check_and_broadcast_for_cc(cc)
    
#     return jsonify({"ok": True, "cc": cc, "subscribed": True})

# @broadcast_bp.route("/broadcast/unsubscribe", methods=["POST"])
# def unsubscribe_broadcast():
#     u = get_current_user()
#     if not u:
#         return jsonify({"message": "Unauthorized"}), 401
#     data = request.get_json(force=True, silent=True) or {}
#     cc = (data.get("cc") or "").strip()
#     if not cc:
#         return jsonify({"message": "cc is required"}), 400
#     sub = BroadcastSubscription.query.filter_by(email=u.email, cc=cc).first()
#     if sub:
#         if sub:
#             db.session.delete(sub)
#             db.session.commit()
#     return jsonify({"ok": True, "cc": cc, "subscribed": False})

# @broadcast_bp.route("/broadcast/subscriptions", methods=["GET"])
# def list_subscriptions():
#     u = get_current_user()
#     if not u:
#         return jsonify({"message": "Unauthorized"}), 401
#     subs = BroadcastSubscription.query.filter_by(email=u.email).all()
#     data = [{"cc": s.cc, "active": s.active, "id": s.id} for s in subs]
#     return jsonify({"subscriptions": data})

# # Handy: pull latest notifications for the current user
# @broadcast_bp.route("/broadcast/notifications", methods=["GET"])
# def my_notifications():
#     u = get_current_user()
#     if not u:
#         return jsonify({"message": "Unauthorized"}), 401
#     rows = (Notification.query
#         .filter_by(receiver_email=u.email)
#         .order_by(Notification.created_at.desc())
#         .limit(50)
#         .all()
#     )
#     data = [{
#         "id": n.id,
#         "message": n.message,
#         "is_read": n.is_read,
#         "created_at": n.created_at.isoformat(),
#         } for n in rows
#     ]
#     return jsonify({"notifications": data})

from flask import Blueprint, jsonify, request

from ..models import Notification, db
from ..services.find_user import get_current_user
from ..services.broadcast_observer import subject, SubscriptionObserver

notification_bp = Blueprint("notifications", __name__, url_prefix="/api")

@notification_bp.route("/broadcast/subscribe", methods=["POST"])
def subscribe_broadcast():
    u = get_current_user()
    if not u:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json(force=True, silent=True) or {}
    cc = (data.get("cc") or "").strip()
    if not cc:
        return jsonify({"message": "cc is required"}), 400

    # In‑memory subscription (no DB row)
    if not subject.find(u.email, cc):
        subject.register(SubscriptionObserver(user_email=u.email, cc=cc, _subject=subject))

    return jsonify({"ok": True, "cc": cc, "subscribed": True})

@notification_bp.route("/broadcast/unsubscribe", methods=["POST"])
def unsubscribe_broadcast():
    u = get_current_user()
    if not u:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json(force=True, silent=True) or {}
    cc = (data.get("cc") or "").strip()
    if not cc:
        return jsonify({"message": "cc is required"}), 400

    obs = subject.find(u.email, cc)
    if obs:
        subject.unregister(obs)

    return jsonify({"ok": True, "cc": cc, "subscribed": False})

@notification_bp.route("/broadcast/subscriptions", methods=["GET"])
def list_subscriptions():
    u = get_current_user()
    if not u:
        return jsonify({"message": "Unauthorized"}), 401

    subs = subject.subscriptions_for_user(u.email)
    # Fake an id for UI purposes
    data = [{"cc": s.cc, "active": True, "id": f"{s.user_email}-{s.cc}"} for s in subs]
    return jsonify({"subscriptions": data})

# Handy: pull latest notifications for the current user (unchanged)
@notification_bp.route("/notifications", methods=["GET"])
def my_notifications():
    u = get_current_user()
    if not u:
        return jsonify({"message": "Unauthorized"}), 401
    
    rows = (Notification.query
        .filter_by(receiver_email=u.email)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    data = [{
        "id": n.id,
        "message": n.message,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat(),
        } for n in rows
    ]
    return jsonify({"notifications": data})