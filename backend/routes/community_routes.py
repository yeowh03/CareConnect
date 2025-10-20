# server/routes/community_routes.py
from flask import Blueprint
from ..controllers.community_controller import CCController as c

community_bp = Blueprint("community", __name__, url_prefix="/api")

@community_bp.get("/community-clubs")
def community_clubs(): return c.community_clubs()
