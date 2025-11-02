"""PostgreSQL Database Implementation for CareConnect Backend.

This module provides PostgreSQL-specific database configuration
for the Factory pattern database abstraction layer.
"""

from .database_interface import DatabaseInterface

class PostgresSQLDatabase(DatabaseInterface):
    """PostgreSQL database implementation.
    
    Configures Flask application to use PostgreSQL database
    with connection string from environment variables.
    """
    def init_app(self, app, db):
        """Initialize Flask app with PostgreSQL configuration.
        
        Args:
            app (Flask): Flask application instance.
            db (SQLAlchemy): SQLAlchemy instance to configure.
            
        Returns:
            SQLAlchemy: Configured database instance.
            
        Raises:
            RuntimeError: If DATABASE_URL is not configured.
        """
        if not app.config.get("SQLALCHEMY_DATABASE_URI"):
            # Expect DATABASE_URL in your env and loaded into Config
            raise RuntimeError("DATABASE_URL must be set for PostgreSQL.")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(app)
        return db
