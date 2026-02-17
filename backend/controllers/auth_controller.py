"""Authentication Controller for CareConnect Backend.

This module handles user authentication using the Strategy pattern,
supporting both Google OAuth and password-based authentication.
"""

from flask import jsonify, redirect, url_for, session, request
from ..extensions import oauth
from ..services.auth_strategies import (
    AuthenticationContext,
    GoogleOAuthStrategy,
    PasswordStrategy
)


class AuthController:
    """Controller class for handling authentication operations.
    
    Uses the Strategy pattern to support multiple authentication methods
    including Google OAuth and password-based authentication.
    """
    def __init__(self):
        self.auth_context = AuthenticationContext()
    
    @staticmethod
    def start_google_login():
        """Initiate Google OAuth flow.
        
        Returns:
            Response: Redirect response to Google OAuth authorization URL.
        """
        redirect_uri = url_for("auth.auth_callback", _external=True)
        return oauth.google.authorize_redirect(redirect_uri)

    @staticmethod
    def google_callback(frontend_origin: str):
        """Handle Google OAuth callback using strategy pattern.
        
        Args:
            frontend_origin (str): Frontend URL for redirect after authentication.
            
        Returns:
            Response: Redirect to frontend or JSON error response.
        """
        auth_context = AuthenticationContext()
        auth_context.set_strategy(GoogleOAuthStrategy())
        
        result, status_code = auth_context.authenticate({})
        
        if status_code == 200 or status_code == 201:
            redirect_path = result.get("redirect", "/clienthome")
            return redirect(frontend_origin + redirect_path)
        else:
            return jsonify(result), status_code

    @staticmethod
    def register_user(data):
        """Register user using password strategy.
        
        Args:
            data (dict): User registration data including email, password, etc.
            
        Returns:
            tuple: JSON response and HTTP status code.
        """
        auth_context = AuthenticationContext()
        auth_context.set_strategy(PasswordStrategy())
        
        result, status_code = auth_context.create_user(data)
        return jsonify(result), status_code

    @staticmethod
    def login_with_password(data):
        """Login using password strategy.
        
        Args:
            data (dict): Login credentials including email and password.
            
        Returns:
            tuple: JSON response and HTTP status code.
        """
        auth_context = AuthenticationContext()
        auth_context.set_strategy(PasswordStrategy())
        
        result, status_code = auth_context.authenticate(data)
        return jsonify(result), status_code

    @staticmethod
    def logout_user():
        """Logout user (strategy-agnostic).
        
        Clears the user session regardless of authentication method used.
        
        Returns:
            tuple: JSON success response and HTTP status code.
        """
        session.clear()
        return jsonify({"ok": True}), 200
