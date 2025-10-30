# backend/services/auth_strategies.py
from abc import ABC, abstractmethod
from flask import jsonify, redirect, url_for, session
from ..extensions import oauth, db
from ..models import User, Client
from ..services.find_user import find_user_by_email
from ..services.password import hash_password, verify_password
from ..services.notification_service import create_notification


class AuthenticationStrategy(ABC):
    """Abstract base class for authentication strategies"""
    
    @abstractmethod
    def authenticate(self, data):
        """Authenticate user with provided data"""
        pass
    
    @abstractmethod
    def create_user(self, data):
        """Create new user with provided data"""
        pass


class GoogleOAuthStrategy(AuthenticationStrategy):
    """Google OAuth authentication strategy"""
    
    def authenticate(self, data):
        """Authenticate using Google OAuth token"""
        try:
            oauth.google.authorize_access_token()
            userinfo_endpoint = oauth.google.load_server_metadata().get("userinfo_endpoint") \
                or "https://openidconnect.googleapis.com/v1/userinfo"
            info = oauth.google.get(userinfo_endpoint).json()
            email = info.get("email")
            
            if not email:
                return {"error": "No email from Google"}, 400
            
            user = find_user_by_email(email)
            if user:
                # Update name if not set
                user.name = user.name or info.get("name")
                db.session.commit()
                session["user_email"] = user.email
                return {"authenticated": True, "user": user, "redirect": "/clienthome"}, 200
            else:
                # Auto-create user for Google OAuth
                return self.create_user(info)
                
        except Exception as e:
            return {"error": f"Google authentication failed: {str(e)}"}, 400
    
    def create_user(self, data):
        """Create user from Google OAuth data"""
        try:
            user = User(
                email=data.get("email"),
                name=data.get("name"),
                role="C"
            )
            db.session.add(user)
            db.session.commit()
            
            client = Client(gmail_acc=True, email=user.email)
            db.session.add(client)
            db.session.commit()
            
            # Welcome notification
            msg = f"Welcome to CareConnect, {user.name}. Your Google account has been linked successfully!"
            create_notification(msg, user.email)
            
            session["user_email"] = user.email
            return {"authenticated": True, "user": user, "redirect": "/clienthome"}, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to create Google user: {str(e)}"}, 500


class PasswordStrategy(AuthenticationStrategy):
    """Email/Password authentication strategy"""
    
    def authenticate(self, data):
        """Authenticate using email and password"""
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return {"error": "Email and password are required"}, 400
        
        user = User.query.get(email)
        if not user or not user.password_hash or not verify_password(password, user.password_hash):
            return {"error": "Invalid credentials"}, 401
        
        session["user_email"] = user.email
        return {"authenticated": True, "role": user.role}, 200
    
    def create_user(self, data):
        """Create user with email/password registration"""
        try:
            # Validate monthly income
            try:
                mi = float(data["monthlyIncome"])
                if mi < 0:
                    raise ValueError
            except (KeyError, ValueError, TypeError):
                return {"error": "Monthly income must be a non-negative number"}, 400
            
            # Check if user already exists
            if User.query.get(data["email"]):
                return {"error": "Email already registered"}, 409
            
            # Create user
            phash = hash_password(data["password"])
            user = User(
                name=data["name"],
                contact_number=data["contactNumber"],
                role="C",
                email=data["email"],
                password_hash=phash,
            )
            db.session.add(user)
            db.session.commit()
            
            # Create client profile
            client = Client(
                monthly_income=float(data["monthlyIncome"]),
                email=data["email"]
            )
            db.session.add(client)
            db.session.commit()
            
            # Notify managers
            managers = User.query.filter(User.role == "M").all()
            if managers:
                msg = (
                    f"New client registration from {user.name} ({user.email}) "
                    "is awaiting verification."
                )
                for m in managers:
                    create_notification(message=msg, receiver_email=m.email)
            
            # Welcome message
            msg = (
                f"Welcome to CareConnect, {user.name}. Our admins will verify your account shortly. "
                "Once verified, you will be able to donate and request (if applicable)."
            )
            create_notification(msg, user.email)
            
            session["user_email"] = user.email
            return {"authenticated": True, "user": user}, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Registration failed: {str(e)}"}, 500


class AuthenticationContext:
    """Context class that uses authentication strategies"""
    
    def __init__(self):
        self._strategy = None
    
    def set_strategy(self, strategy: AuthenticationStrategy):
        """Set the authentication strategy"""
        self._strategy = strategy
    
    def authenticate(self, data):
        """Authenticate using current strategy"""
        if not self._strategy:
            return {"error": "No authentication strategy set"}, 500
        return self._strategy.authenticate(data)
    
    def create_user(self, data):
        """Create user using current strategy"""
        if not self._strategy:
            return {"error": "No authentication strategy set"}, 500
        return self._strategy.create_user(data)