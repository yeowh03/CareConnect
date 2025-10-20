# backend/database/sqlite_database.py
from .database_interface import DatabaseInterface

class SQLiteDatabase(DatabaseInterface):
    def init_app(self, app, db):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(app)
        return db
