# server/controllers/profile_controller.py
from flask import jsonify, session
from ..extensions import db
from ..models import User, Client, Manager
from ..services.find_user import get_current_user, find_client_by_email, find_manager_by_email
from ..services.password import hash_password
from ..services.notification_service import create_notification

class ProfileController:
    def me():
        u = get_current_user()
        if not u:
            return jsonify({"authenticated": False, "message":"Not authenticated!"}), 400
        # if u.role == "C":
            # c = find_client_by_email(session["user_email"])
            # return jsonify({"authenticated": True, "email": u.email, "role": u.role, "monthly_income": c.monthly_income}), 200
        return jsonify({"authenticated": True, "email": u.email, "role": u.role}), 200

    def update_profile(data):
        u = get_current_user()
        if not u:
            return jsonify({"error": "Unauthorized"}), 401
        c = find_client_by_email(u.email)

        income_changed = False

        if "name" in data: u.name = data["name"]
        if "contactNumber" in data: u.contact_number = data["contactNumber"]
        if "monthlyIncome" in data:
            try:
                mi = float(data["monthlyIncome"])
                if mi < 0: raise ValueError
                if c: 
                    # if change income, must verify again
                    if c.monthly_income != mi:
                        c.monthly_income = mi
                        c.account_status = "Pending"
                        income_changed = True
            except Exception:
                return jsonify({"error": "monthly_income must be non-negative"}), 400
        if "password" in data: u.password_hash = hash_password(data["password"])
        if "email" in data: u.email = data["email"]
        db.session.commit()

        # If monthly income changed, notify all managers to re-verify this user
        if income_changed:
            managers = User.query.filter(User.role == "M").all()
            if managers:
                msg = (
                    f"Client {u.name} ({u.email}) updated monthly income and requires re-verification."
                )
                for m in managers:
                    create_notification(
                        message=msg,
                        receiver_email=m.email
                    )

        return jsonify({"ok": True}), 200

    def get_client_profile(user_email):
        client, user = db.session.query(Client, User).join(User).filter(Client.email == user_email).first()
        profile_complete = bool(user.email and user.name and user.contact_number and client.monthly_income)
        return jsonify({
            "email": user.email, "name": user.name, "contact_number": user.contact_number,
            "monthly_income": client.monthly_income, "profile_complete": profile_complete,
            "gmail_acc": client.gmail_acc, "role": "C", "account_status": client.account_status
        })

    def get_manager_profile(user_email):
        manager, user = db.session.query(Manager, User).join(User).filter(Manager.email == user_email).first()
        return jsonify({
            "email": user.email, "name": user.name, "contact_number": user.contact_number,
            "cc": manager.cc, "profile_complete": True, "role": "M"
        })

    def list_pending_registrations():
        rows = db.session.query(Client, User).join(User).filter(Client.account_status == "Pending").all()
        out = []
        for client, user in rows:
            out.append({"client": {"email": client.email, "monthly_income": client.monthly_income},
                        "user": {"contact_number": user.contact_number, "name": user.name}})
            print(out)
        return jsonify(out)

    def process_registrations(outcome: bool, email: str):
        c = Client.query.get(email)
        if not c: return jsonify({"error": "Client not found"}), 404

        u = User.query.get(email)

        try:
            if outcome:
                c.account_status = "Confirmed"
                db.session.commit()

                # Notify user: approved
                msg = "Your registration has been approved. Welcome aboard! View the map and select the CC to make a new donation or request (if applicable)."
                create_notification(
                    message=msg,
                    receiver_email=email
                )
            else:
                # Notify user: rejected
                c.account_status = "Rejected"
                db.session.commit()

                name = u.name if u else email             
                msg = (
                    f"Hi {name}, your registration has been rejected. "
                    "You may re-apply with updated information."
                )
                create_notification(
                    message=msg,
                    receiver_email=email
                )

            return jsonify({"ok": True})
        
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to process registration", "details": str(e)}), 500
