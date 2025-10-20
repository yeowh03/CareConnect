# backend/extensions.py
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS
from flask_session import Session as FlaskSession
from supabase import create_client

db = SQLAlchemy()        # ← single shared instance
oauth = OAuth()

def init_cors(app, origin):
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": [origin]}})

def init_session(app, session_type, redis_url, env):
    from redis import from_url as redis_from_url
    app.config["SESSION_TYPE"] = session_type
    if session_type == "redis":
        app.config["SESSION_REDIS"] = redis_from_url(redis_url)
    app.config["SESSION_COOKIE_NAME"] = "session"
    if env == "production":
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
        app.config["SESSION_COOKIE_SECURE"] = True
    else:
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_PERMANENT"] = False
    FlaskSession(app)

def init_oauth(app, client_id, client_secret):
    oauth.init_app(app)
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=client_id,
        client_secret=client_secret,
        client_kwargs={"scope": "openid email profile"},
    )

def init_supabase(url, key):
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    return create_client(url, key)
