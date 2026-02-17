"""Database Factory for CareConnect Backend.

This module implements the Factory pattern to create database instances
based on configuration. Supports SQLite and PostgreSQL databases.
"""

from .sqlite_database import SQLiteDatabase
from .postgres_database import PostgresSQLDatabase

class DatabaseFactory:
    """Factory class for creating database instances.
    
    Uses the Factory pattern to instantiate the appropriate database
    implementation based on the specified database type.
    """
    @staticmethod
    def getDatabase(db_type: str):
        """Create a database instance based on the specified type.
        
        Args:
            db_type (str): Database type - 'sqlite' or 'postgres'/'postgresql'.
            
        Returns:
            Database implementation instance.
            
        Raises:
            ValueError: If unsupported database type is specified.
        """
        t = (db_type or "").lower()
        if t == "sqlite":
            print("Using SQLite database...")
            return SQLiteDatabase()
        if t in ("postgres", "postgresql"):
            print("Using PostgreSQL database...")
            return PostgresSQLDatabase()
        raise ValueError(f"Unsupported database type: {db_type}")
