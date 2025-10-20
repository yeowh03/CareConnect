# backend/database/database_interface.py
from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    @abstractmethod
    def init_app(self, app, db):
        """Configure app for this database and bind the shared SQLAlchemy instance."""
        pass
