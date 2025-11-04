"""Authentication Routes for CareConnect Backend.

This module defines Flask routes for user authentication including
Google OAuth, password-based login, registration, and logout.
"""

from flask import Blueprint, request
from ..controllers.auth_controller import AuthController as c
from ..config import Config

auth_bp = Blueprint("auth", __name__, url_prefix="/api")

# Google OAuth login initiation
@auth_bp.get("/login")
def login_google(): 
    return c.start_google_login()

# Google OAuth callback handler
@auth_bp.get("/auth/callback")
def auth_callback(): 
    return c.google_callback(Config.FRONTEND_ORIGIN)

# User registration with email/password
@auth_bp.post("/register")
def register(): 
    return c.register_user(request.get_json(force=True, silent=True) or {})

# Email/password login
@auth_bp.post("/login_password")
def login_password(): 
    return c.login_with_password(request.get_json(force=True, silent=True) or {})

# User logout (clears session)
@auth_bp.post("/logout")
def logout(): 
    return c.logout_user()
