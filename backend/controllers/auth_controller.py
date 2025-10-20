# server/controllers/auth_controller.py
from flask import jsonify, redirect, url_for, session, request
from ..extensions import oauth
from ..models import User, Client
from ..extensions import db
from ..services.find_user import find_user_by_email
from ..services.password import hash_password, verify_password

class AuthController:
    def start_google_login():
        redirect_uri = url_for("auth.auth_callback", _external=True)
        return oauth.google.authorize_redirect(redirect_uri)

    def google_callback(frontend_origin: str):
        oauth.google.authorize_access_token()
        userinfo_endpoint = oauth.google.load_server_metadata().get("userinfo_endpoint") \
            or "https://openidconnect.googleapis.com/v1/userinfo"
        info = oauth.google.get(userinfo_endpoint).json()
        email = info.get("email")
        if not email:
            return jsonify({"error": "No email from Google"}), 400

        user = find_user_by_email(email)
        if not user:
            user = User(email=email, name=info.get("name"), role="C")
            db.session.add(user); db.session.commit()
            client = Client(gmail_acc=True, email=email)
            db.session.add(client); db.session.commit()
        else:
            user.name = user.name or info.get("name")
            db.session.commit()

        session["user_email"] = user.email
        return redirect(frontend_origin + "/clienthome")

    def register_user(data):
        try:
            mi = float(data["monthlyIncome"])
            if mi < 0: raise ValueError
        except Exception:
            return jsonify({"error": "monthly_income must be a non-negative number"}), 400

        if User.query.get(data["email"]):
            return jsonify({"error": "Email already registered"}), 409

        phash = hash_password(data["password"])
        user = User(
            name=data["name"], contact_number=data["contactNumber"], role="C",
            email=data["email"], password_hash=phash,
        )
        db.session.add(user); db.session.commit()

        client = Client(monthly_income=float(data["monthlyIncome"]), email=data["email"])
        db.session.add(client); db.session.commit()

        session["user_email"] = user.email
        return jsonify({"ok": True}), 200

    def login_with_password(data):
        email, password = data.get("email"), data.get("password")
        if not email or not password:
            return jsonify({"error": "email and password are required"}), 400
        user = User.query.get(email)
        if not user or not user.password_hash or not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid credentials"}), 401
        session["user_email"] = user.email
        return jsonify({"role": user.role}), 200

    def logout_user():
        session.clear()
        return jsonify({"ok": True}), 200
