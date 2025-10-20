# server/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "donations")

    # OAuth (Google)
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    # Environment
    ENV = os.getenv("FLASK_ENV", "development")
