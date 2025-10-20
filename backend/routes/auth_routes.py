# server/routes/auth_routes.py
from flask import Blueprint, request
from ..controllers.auth_controller import AuthController as c
from ..config import Config

auth_bp = Blueprint("auth", __name__, url_prefix="/api")

@auth_bp.get("/login")
def login_google(): return c.start_google_login()

@auth_bp.get("/auth/callback")
def auth_callback(): return c.google_callback(Config.FRONTEND_ORIGIN)

@auth_bp.post("/register")
def register(): return c.register_user(request.get_json(force=True, silent=True) or {})

@auth_bp.post("/login_password")
def login_password(): return c.login_with_password(request.get_json(force=True, silent=True) or {})

@auth_bp.post("/logout")
def logout(): return c.logout_user()
