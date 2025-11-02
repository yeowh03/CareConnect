"""Community Routes for CareConnect Backend.

This module defines Flask routes for community club data retrieval
including location information and fulfillment statistics.
"""

from flask import Blueprint
from ..controllers.community_controller import CCController as c

community_bp = Blueprint("community", __name__, url_prefix="/api")

@community_bp.get("/community-clubs")
def community_clubs(): return c.community_clubs()
