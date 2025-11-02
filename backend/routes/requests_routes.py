"""Request Routes for CareConnect Backend.

This module defines Flask routes for request management including
creation, updates, completion workflow, and CRUD operations.
"""

from flask import Blueprint
from ..controllers.requests_controller import RequestController as c

requests_bp = Blueprint("requests", __name__, url_prefix="/api")

@requests_bp.post("/requests")
def create_request(): return c.create_request()

@requests_bp.get("/my_requests")
def my_requests(): return c.my_requests()

@requests_bp.post("/requests/reject")
def reject_matched_request(): return c.reject_matched_request()

@requests_bp.get("/manager/matched_requests")
def manager_matched_requests(): return c.manager_matched_requests()

@requests_bp.post("/manager/requests/<int:req_id>/complete")
def manager_complete_request(req_id): return c.manager_complete_request(req_id)

@requests_bp.get("/requests/<int:req_id>")
def get_my_request(req_id): return c.get_my_request(req_id)

@requests_bp.patch("/requests/<int:req_id>")
def update_pending_request(req_id): return c.update_pending_request(req_id)

@requests_bp.delete("/requests/<int:req_id>")
def delete_pending_request(req_id): return c.delete_pending_request(req_id)
