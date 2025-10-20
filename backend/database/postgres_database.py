# backend/database/postgres_database.py
from .database_interface import DatabaseInterface

class PostgresSQLDatabase(DatabaseInterface):
    def init_app(self, app, db):
        if not app.config.get("SQLALCHEMY_DATABASE_URI"):
            # Expect DATABASE_URL in your env and loaded into Config
            raise RuntimeError("DATABASE_URL must be set for PostgreSQL.")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(app)
        return db
