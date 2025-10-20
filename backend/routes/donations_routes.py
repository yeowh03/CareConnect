# server/routes/donations_routes.py
from flask import Blueprint, current_app
from ..controllers.donations_controller import DonationController as c
from ..extensions import init_supabase
from ..config import Config

donations_bp = Blueprint("donations", __name__, url_prefix="/api")

def _supabase():
    # lazily create once and cache on app
    if not hasattr(current_app, "_supabase"):
        current_app._supabase = init_supabase(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
    return current_app._supabase

@donations_bp.post("/donations")
def create_donation(): return c.create_donation(_supabase(), Config.SUPABASE_BUCKET)

@donations_bp.get("/my_donations")
def my_donations(): return c.my_donations()

@donations_bp.get("/manager/donations")
def manager_list(): return c.manager_list_donations()

@donations_bp.post("/manager/donations/<int:donation_id>/approve")
def manager_approve(donation_id): return c.manager_approve(donation_id)

@donations_bp.delete("/manager/donations/<int:donation_id>/reject")
def manager_reject(donation_id): return c.manager_reject(donation_id)

@donations_bp.post("/manager/donations/<int:donation_id>/add")
def manager_add(donation_id): return c.manager_add(donation_id)

@donations_bp.get("/donations/<int:donation_id>")
def get_my_donation(donation_id): return c.get_my_donation(donation_id)

@donations_bp.patch("/donations/<int:donation_id>")
def update_pending_donation(donation_id): 
    return c.update_pending_donation(donation_id, _supabase(), Config.SUPABASE_BUCKET)

@donations_bp.delete("/donations/<int:donation_id>")
def delete_pending_or_approved(donation_id): return c.delete_pending_or_approved(donation_id)
