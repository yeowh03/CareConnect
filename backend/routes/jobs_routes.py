"""Jobs Routes for CareConnect Backend.

This module defines Flask routes for background job management
including manual job triggers and status monitoring.
"""

from flask import Blueprint, jsonify, request
from ..controllers.jobs_controller import JobsController

jobs_bp = Blueprint("jobs", __name__, url_prefix="/admin/jobs")

# ------------- Routes -------------
@jobs_bp.get("/status")
def get_status():
    """Return current job status summary."""
    return jsonify(JobsController.get_status())

@jobs_bp.get("/run/cleanup")
def run_cleanup_now():
    print("yeyey")
    result = JobsController.run_cleanup_now()
    print("yeyeysss")
    return jsonify(result)


@jobs_bp.post("/run/expiry")
def run_expiry_now():
    days = int(request.args.get("days", 2))
    result = JobsController.run_expiry_now(days=days)
    return jsonify(result)

@jobs_bp.post("/run/cleanup-approved")
def run_cleanup_approved_donations_now():
    days = int(request.args.get("days", 2))
    result = JobsController.run_cleanup_approved_donations_now(days=days)
    return jsonify(result)
