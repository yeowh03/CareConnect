"""Jobs Routes for CareConnect Backend.

This module defines Flask routes for background job management
including manual job triggers and status monitoring.
"""

from flask import Blueprint, jsonify, request
from ..controllers.jobs_controller import JobsController

jobs_bp = Blueprint("jobs", __name__, url_prefix="/admin/jobs")

# Get status of all background jobs
@jobs_bp.get("/status")
def get_status():
    """Return current job status summary."""
    return jsonify(JobsController.get_status())

# Manually trigger cleanup of expired items
@jobs_bp.get("/run/cleanup")
def run_cleanup_now():
    result = JobsController.run_cleanup_now()
    return jsonify(result)

# Manually trigger expiry of old matched requests
@jobs_bp.post("/run/expiry")
def run_expiry_now():
    days = int(request.args.get("days", 2))  # Default 2 days until expiry
    result = JobsController.run_expiry_now(days=days)
    return jsonify(result)

# Manually trigger cleanup of old approved donations
@jobs_bp.post("/run/cleanup-approved")
def run_cleanup_approved_donations_now():
    days = int(request.args.get("days", 2))  # Default 2 days until cleanup
    result = JobsController.run_cleanup_approved_donations_now(days=days)
    return jsonify(result)
