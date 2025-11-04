"""Request Routes for CareConnect Backend.

This module defines Flask routes for request management including
creation, updates, completion workflow, and CRUD operations.
"""

from flask import Blueprint
from ..controllers.requests_controller import RequestController as c

requests_bp = Blueprint("requests", __name__, url_prefix="/api")

# Create new request and trigger allocation
@requests_bp.post("/requests")
def create_request(): 
    return c.create_request()

# Get current user's requests
@requests_bp.get("/my_requests")
def my_requests(): 
    return c.my_requests()

# Client: Reject a matched request and free items
@requests_bp.post("/requests/reject")
def reject_matched_request(): 
    return c.reject_matched_request()

# Manager: Get matched requests for their CC
@requests_bp.get("/manager/matched_requests")
def manager_matched_requests(): 
    return c.manager_matched_requests()

# Manager: Mark matched request as completed
@requests_bp.post("/manager/requests/<int:req_id>/complete")
def manager_complete_request(req_id): 
    return c.manager_complete_request(req_id)

# Get specific request details for current user
@requests_bp.get("/requests/<int:req_id>")
def get_my_request(req_id): 
    return c.get_my_request(req_id)

# Update pending request details
@requests_bp.patch("/requests/<int:req_id>")
def update_pending_request(req_id): 
    return c.update_pending_request(req_id)

# Delete pending request and free any allocated items
@requests_bp.delete("/requests/<int:req_id>")
def delete_pending_request(req_id): 
    return c.delete_pending_request(req_id)
