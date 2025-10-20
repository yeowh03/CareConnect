# backend/database/database_factory.py
from .sqlite_database import SQLiteDatabase
from .postgres_database import PostgresSQLDatabase

class DatabaseFactory:
    @staticmethod
    def getDatabase(db_type: str):
        t = (db_type or "").lower()
        if t == "sqlite":
            print("Using SQLite database...")
            return SQLiteDatabase()
        if t in ("postgres", "postgresql"):
            print("Using PostgreSQL database...")
            return PostgresSQLDatabase()
        raise ValueError(f"Unsupported database type: {db_type}")
