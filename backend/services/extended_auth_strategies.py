# backend/services/extended_auth_strategies.py
"""
Extended authentication strategies demonstrating the flexibility of the strategy pattern.
These can be easily plugged into the existing AuthenticationContext.
"""

from .auth_strategies import AuthenticationStrategy
from flask import session
from ..extensions import db
from ..models import User, Client
from ..services.notification_service import create_notification
import jwt
import requests


class FacebookOAuthStrategy(AuthenticationStrategy):
    """Facebook OAuth authentication strategy"""
    
    def authenticate(self, data):
        """Authenticate using Facebook OAuth token"""
        try:
            access_token = data.get("access_token")
            if not access_token:
                return {"error": "Facebook access token required"}, 400
            
            # Verify token with Facebook
            response = requests.get(
                f"https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}"
            )
            
            if response.status_code != 200:
                return {"error": "Invalid Facebook token"}, 401
            
            fb_data = response.json()
            email = fb_data.get("email")
            
            if not email:
                return {"error": "No email from Facebook"}, 400
            
            user = User.query.get(email)
            if user:
                session["user_email"] = user.email
                return {"authenticated": True, "user": user, "redirect": "/clienthome"}, 200
            else:
                return self.create_user(fb_data)
                
        except Exception as e:
            return {"error": f"Facebook authentication failed: {str(e)}"}, 400
    
    def create_user(self, data):
        """Create user from Facebook OAuth data"""
        try:
            user = User(
                email=data.get("email"),
                name=data.get("name"),
                role="C"
            )
            db.session.add(user)
            db.session.commit()
            
            client = Client(gmail_acc=False, email=user.email)
            db.session.add(client)
            db.session.commit()
            
            msg = f"Welcome to CareConnect, {user.name}. Your Facebook account has been linked successfully!"
            create_notification(msg, user.email)
            
            session["user_email"] = user.email
            return {"authenticated": True, "user": user, "redirect": "/clienthome"}, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to create Facebook user: {str(e)}"}, 500


class JWTTokenStrategy(AuthenticationStrategy):
    """JWT token-based authentication strategy"""
    
    def __init__(self, secret_key):
        self.secret_key = secret_key
    
    def authenticate(self, data):
        """Authenticate using JWT token"""
        try:
            token = data.get("token")
            if not token:
                return {"error": "JWT token required"}, 400
            
            # Decode and verify JWT
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            email = payload.get("email")
            
            if not email:
                return {"error": "Invalid token payload"}, 401
            
            user = User.query.get(email)
            if not user:
                return {"error": "User not found"}, 404
            
            session["user_email"] = user.email
            return {"authenticated": True, "role": user.role}, 200
            
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}, 401
        except Exception as e:
            return {"error": f"JWT authentication failed: {str(e)}"}, 400
    
    def create_user(self, data):
        """JWT strategy doesn't support user creation"""
        return {"error": "User creation not supported with JWT strategy"}, 400


class APIKeyStrategy(AuthenticationStrategy):
    """API key authentication strategy for service-to-service communication"""
    
    def authenticate(self, data):
        """Authenticate using API key"""
        try:
            api_key = data.get("api_key")
            service_name = data.get("service_name")
            
            if not api_key or not service_name:
                return {"error": "API key and service name required"}, 400
            
            # In a real implementation, you'd validate against a database of API keys
            valid_keys = {
                "donation_service": "dk_12345",
                "notification_service": "nk_67890",
                "allocation_service": "ak_54321"
            }
            
            if valid_keys.get(service_name) != api_key:
                return {"error": "Invalid API key"}, 401
            
            # For service accounts, we might not use sessions
            return {"authenticated": True, "service": service_name}, 200
            
        except Exception as e:
            return {"error": f"API key authentication failed: {str(e)}"}, 400
    
    def create_user(self, data):
        """API key strategy doesn't support user creation"""
        return {"error": "User creation not supported with API key strategy"}, 400


class MultiFactorStrategy(AuthenticationStrategy):
    """Multi-factor authentication strategy"""
    
    def authenticate(self, data):
        """Authenticate using email/password + OTP"""
        try:
            email = data.get("email")
            password = data.get("password")
            otp_code = data.get("otp_code")
            
            if not all([email, password, otp_code]):
                return {"error": "Email, password, and OTP code required"}, 400
            
            # First, verify password (reuse PasswordStrategy logic)
            from .auth_strategies import PasswordStrategy
            password_strategy = PasswordStrategy()
            result, status = password_strategy.authenticate({"email": email, "password": password})
            
            if status != 200:
                return result, status
            
            # Then verify OTP (simplified - in reality, you'd check against stored OTP)
            if not self._verify_otp(email, otp_code):
                return {"error": "Invalid OTP code"}, 401
            
            return result, status
            
        except Exception as e:
            return {"error": f"Multi-factor authentication failed: {str(e)}"}, 400
    
    def create_user(self, data):
        """Create user with MFA enabled"""
        try:
            # First create user with password strategy
            from .auth_strategies import PasswordStrategy
            password_strategy = PasswordStrategy()
            result, status = password_strategy.create_user(data)
            
            if status == 201:
                # Enable MFA for the new user
                email = data.get("email")
                self._setup_mfa(email)
                result["mfa_enabled"] = True
            
            return result, status
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"MFA user creation failed: {str(e)}"}, 500
    
    def _verify_otp(self, email, otp_code):
        """Verify OTP code (simplified implementation)"""
        # In a real implementation, you'd check against TOTP or stored codes
        return otp_code == "123456"  # Simplified for demo
    
    def _setup_mfa(self, email):
        """Setup MFA for user (simplified implementation)"""
        # In a real implementation, you'd generate TOTP secret, send setup instructions
        msg = f"Multi-factor authentication has been enabled for your account. Please configure your authenticator app."
        create_notification(msg, email)