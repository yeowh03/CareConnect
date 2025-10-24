# backend/app.py
import os
from flask import Flask
from backend.config import Config
from backend.extensions import db, init_cors, init_session, init_oauth
from backend.database.database_factory import DatabaseFactory
# from backend.utils import start_cleanup_expired_items_daemon
# from backend.utils import start_allocator_daemon
# from backend.utils import start_expire_matched_requests_daemon

# import blueprints AFTER config/factory lines is fine
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
    app = Flask(__name__)
    app.config.from_object(Config)

    # Sessions & CORS
    init_session(app, Config.SESSION_TYPE, Config.REDIS_URL, Config.ENV)
    init_cors(app, Config.FRONTEND_ORIGIN)

    # --- Database via Factory (bind the shared db) ---
    db_type = "postgres"  # "sqlite" or "postgres"
    impl = DatabaseFactory.getDatabase(db_type)
    impl.init_app(app, db)  # ← binds the shared db instance

    # Create tables
    with app.app_context():
        db.create_all()

    # OAuth
    init_oauth(app, Config.GOOGLE_CLIENT_ID, Config.GOOGLE_CLIENT_SECRET)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(donations_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(inventory_bp)

    # start_allocator_daemon(app, every_minutes=1)
    # start_cleanup_expired_items_daemon(app, run_at_hour_sg=0, run_at_minute_sg=0)
    # start_expire_matched_requests_daemon(app, run_at_hour_sg=0, run_at_minute_sg=0)

    JobsController.start_schedulers(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_RUN_PORT", "5000")),
        debug=(Config.ENV != "production"),
        use_reloader=False,
    )
