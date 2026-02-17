"""CareConnect Backend Application.

This module contains the Flask application factory for the CareConnect backend.
It configures the database, authentication, CORS, and registers all route blueprints.
"""

import os
from flask import Flask
from backend.config import Config
from backend.extensions import db, init_cors, init_session, init_oauth
from backend.database.database_factory import DatabaseFactory

from backend.routes.auth_routes import auth_bp
from backend.routes.profile_routes import profile_bp
from backend.routes.donations_routes import donations_bp
from backend.routes.requests_routes import requests_bp
from backend.routes.community_routes import community_bp
from backend.routes.jobs_routes import jobs_bp
from backend.routes.notification_routes import notification_bp
from backend.routes.inventory_routes import inventory_bp

from .controllers.jobs_controller import JobsController

def create_app():
    """Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize session management and CORS
    init_session(app, Config.SESSION_TYPE, Config.REDIS_URL, Config.ENV)
    init_cors(app, Config.FRONTEND_ORIGIN)

    # Initialize database using Factory pattern
    db_type = "postgres"  # Switch between "sqlite" and "postgres"
    impl = DatabaseFactory.getDatabase(db_type)
    impl.init_app(app, db)  # Bind the shared SQLAlchemy instance

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    # Initialize Google OAuth
    init_oauth(app, Config.GOOGLE_CLIENT_ID, Config.GOOGLE_CLIENT_SECRET)

    # Register all API route blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(donations_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(inventory_bp)

    # Start background job schedulers
    JobsController.start_schedulers(app)
    return app

app = create_app()

# Run the application if executed directly
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",  # Accept connections from any IP
        port=int(os.getenv("FLASK_RUN_PORT", "5000")),  # Default to port 5000
        debug=(Config.ENV != "production"),  # Enable debug mode in development
        use_reloader=False,  # Disable reloader to prevent scheduler conflicts
    )
