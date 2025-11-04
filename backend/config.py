"""Configuration Module for CareConnect Backend.

This module contains the configuration class that loads environment variables
for database connections, OAuth settings, and other application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for Flask application settings.
    
    Loads configuration from environment variables including:
    - Database connection settings
    - OAuth credentials
    - Session configuration
    - Supabase storage settings
    """
    # Flask application settings
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable event system for performance

    # Supabase storage configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "donations")

    # Google OAuth credentials
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    # Application environment
    ENV = os.getenv("FLASK_ENV", "development")
