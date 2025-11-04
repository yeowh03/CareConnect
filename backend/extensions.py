"""Flask Extensions and Initialization Functions.

This module contains Flask extension instances and initialization functions
for CORS, sessions, OAuth, and Supabase client configuration.
"""

from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS
from flask_session import Session as FlaskSession
from supabase import create_client

# Global extension instances
db = SQLAlchemy()        # Shared SQLAlchemy instance for database operations
oauth = OAuth()          # OAuth client for Google authentication

def init_cors(app, origin):
    """Initialize CORS for the Flask application.
    
    Args:
        app (Flask): Flask application instance.
        origin (str): Allowed origin for CORS requests.
    """
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": [origin]}})

def init_session(app, session_type, redis_url, env):
    """Initialize Flask session configuration.
    
    Args:
        app (Flask): Flask application instance.
        session_type (str): Session storage type ('redis' or 'filesystem').
        redis_url (str): Redis connection URL for redis session type.
        env (str): Environment ('production' or 'development').
    """
    from redis import from_url as redis_from_url
    app.config["SESSION_TYPE"] = session_type
    
    # Configure Redis for session storage if specified
    if session_type == "redis":
        app.config["SESSION_REDIS"] = redis_from_url(redis_url)
    
    # Set session cookie configuration
    app.config["SESSION_COOKIE_NAME"] = "session"
    
    # Configure cookie security based on environment
    if env == "production":
        app.config["SESSION_COOKIE_SAMESITE"] = "None"  # Allow cross-site cookies
        app.config["SESSION_COOKIE_SECURE"] = True      # Require HTTPS
    else:
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"   # Same-site for development
        app.config["SESSION_COOKIE_SECURE"] = False     # Allow HTTP in development
    
    app.config["SESSION_PERMANENT"] = False  # Sessions expire when browser closes
    FlaskSession(app)

def init_oauth(app, client_id, client_secret):
    """Initialize OAuth configuration for Google authentication.
    
    Args:
        app (Flask): Flask application instance.
        client_id (str): Google OAuth client ID.
        client_secret (str): Google OAuth client secret.
    """
    oauth.init_app(app)
    
    # Register Google OAuth provider with OpenID Connect
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=client_id,
        client_secret=client_secret,
        client_kwargs={"scope": "openid email profile"},  # Request basic profile info
    )

def init_supabase(url, key):
    """Initialize Supabase client for file storage.
    
    Args:
        url (str): Supabase project URL.
        key (str): Supabase service key.
        
    Returns:
        Supabase client instance.
        
    Raises:
        RuntimeError: If URL or key are not provided.
    """
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    return create_client(url, key)
