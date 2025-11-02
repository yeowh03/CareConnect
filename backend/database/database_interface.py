"""Database Interface for CareConnect Backend.

This module defines the abstract interface that all database
implementations must follow in the Factory pattern.
"""

from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    """Abstract interface for database implementations.
    
    Defines the contract that all database types (SQLite, PostgreSQL, etc.)
    must implement for the Factory pattern.
    """
    @abstractmethod
    def init_app(self, app, db):
        """Configure Flask app for this database type.
        
        Args:
            app (Flask): Flask application instance.
            db (SQLAlchemy): Shared SQLAlchemy instance to configure.
            
        Returns:
            SQLAlchemy: Configured database instance.
        """
        pass
