"""Authentication Strategies for CareConnect Backend.

This module implements the Strategy pattern for authentication,
supporting multiple authentication methods including Google OAuth
and traditional email/password authentication.
"""

from abc import ABC, abstractmethod
from flask import jsonify, redirect, url_for, session
from ..extensions import oauth, db
from ..models import User, Client
from ..services.find_user import find_user_by_email
from ..services.password import hash_password, verify_password
from ..services.notification_strategies import DatabaseNotificationStrategy


class AuthenticationStrategy(ABC):
    """Abstract base class for authentication strategies.
    
    Defines the interface that all authentication strategies must implement.
    """
    
    @abstractmethod
    def authenticate(self, data):
        """Authenticate user with provided data.
        
        Args:
            data (dict): Authentication data.
            
        Returns:
            tuple: Response dict and HTTP status code.
        """
        pass
    
    @abstractmethod
    def create_user(self, data):
        """Create new user with provided data.
        
        Args:
            data (dict): User creation data.
            
        Returns:
            tuple: Response dict and HTTP status code.
        """
        pass


class GoogleOAuthStrategy(AuthenticationStrategy):
    """Google OAuth authentication strategy.
    
    Handles authentication and user creation using Google OAuth tokens.
    """
    
    def authenticate(self, data):
        """Authenticate using Google OAuth token.
        
        Args:
            data (dict): OAuth data (unused, token comes from OAuth flow).
            
        Returns:
            tuple: Authentication result and HTTP status code.
        """
        try:
            # Exchange authorization code for access token
            oauth.google.authorize_access_token()
            
            # Get user info endpoint from Google's metadata
            userinfo_endpoint = oauth.google.load_server_metadata().get("userinfo_endpoint") \
                or "https://openidconnect.googleapis.com/v1/userinfo"
            
            # Fetch user information from Google
            info = oauth.google.get(userinfo_endpoint).json()
            email = info.get("email")
            
            if not email:
                return {"error": "No email from Google"}, 400
            
            # Check if user already exists
            user = find_user_by_email(email)
            if user:
                # Update name if not previously set
                user.name = user.name or info.get("name")
                db.session.commit()
                session["user_email"] = user.email
                return {"authenticated": True, "redirect": "/clienthome"}, 200
            else:
                # Auto-create new user for Google OAuth
                return self.create_user(info)
                
        except Exception as e:
            return {"error": f"Google authentication failed: {str(e)}"}, 400
    
    def create_user(self, data):
        """Create user from Google OAuth data.
        
        Args:
            data (dict): Google user info from OAuth.
            
        Returns:
            tuple: User creation result and HTTP status code.
        """
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
            notification_strategy = DatabaseNotificationStrategy()
            notification_strategy.create_notification(msg, user.email)
            
            session["user_email"] = user.email
            return {"authenticated": True, "redirect": "/clienthome"}, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to create Google user: {str(e)}"}, 500


class PasswordStrategy(AuthenticationStrategy):
    """Email/Password authentication strategy.
    
    Handles traditional email and password authentication and registration.
    """
    
    def authenticate(self, data):
        """Authenticate using email and password.
        
        Args:
            data (dict): Login credentials with email and password.
            
        Returns:
            tuple: Authentication result and HTTP status code.
        """
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
        """Create user with email/password registration.
        
        Args:
            data (dict): Registration data including email, password, etc.
            
        Returns:
            tuple: Registration result and HTTP status code.
        """
        try:
            # Validate monthly income input
            try:
                mi = float(data["monthlyIncome"])
                if mi < 0:
                    raise ValueError
            except (KeyError, ValueError, TypeError):
                return {"error": "Monthly income must be a non-negative number"}, 400
            
            # Check for duplicate email registration
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
                notification_strategy = DatabaseNotificationStrategy()
                for m in managers:
                    notification_strategy.create_notification(message=msg, receiver_email=m.email)
            
            # Welcome message
            msg = (
                f"Welcome to CareConnect, {user.name}. Our admins will verify your account shortly. "
                "Once verified, you will be able to donate and request (if applicable)."
            )
            notification_strategy.create_notification(msg, user.email)
            
            session["user_email"] = user.email
            return {"authenticated": True}, 201
        
        except Exception as e:
            db.session.rollback()
            return {"error": f"Registration failed: {str(e)}"}, 500


class AuthenticationContext:
    """Context class that uses authentication strategies.
    
    Implements the Strategy pattern by allowing different authentication
    strategies to be set and used interchangeably.
    """
    
    def __init__(self):
        self._strategy = None
    
    def set_strategy(self, strategy: AuthenticationStrategy):
        """Set the authentication strategy.
        
        Args:
            strategy (AuthenticationStrategy): Strategy to use for authentication.
        """
        self._strategy = strategy
    
    def authenticate(self, data):
        """Authenticate using current strategy.
        
        Args:
            data (dict): Authentication data.
            
        Returns:
            tuple: Authentication result and HTTP status code.
        """
        if not self._strategy:
            return {"error": "No authentication strategy set"}, 500
        return self._strategy.authenticate(data)
    
    def create_user(self, data):
        """Create user using current strategy.
        
        Args:
            data (dict): User creation data.
            
        Returns:
            tuple: User creation result and HTTP status code.
        """
        if not self._strategy:
            return {"error": "No authentication strategy set"}, 500
        return self._strategy.create_user(data)
    
