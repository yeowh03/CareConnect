"""SQLite Database Implementation for CareConnect Backend.

This module provides SQLite-specific database configuration
for the Factory pattern database abstraction layer.
"""

from .database_interface import DatabaseInterface

class SQLiteDatabase(DatabaseInterface):
    """SQLite database implementation.
    
    Configures Flask application to use SQLite database
    with appropriate connection settings.
    """
    def init_app(self, app, db):
        """Initialize Flask app with SQLite configuration.
        
        Args:
            app (Flask): Flask application instance.
            db (SQLAlchemy): SQLAlchemy instance to configure.
            
        Returns:
            SQLAlchemy: Configured database instance.
        """
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(app)
        return db
