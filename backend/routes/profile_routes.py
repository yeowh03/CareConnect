# server/routes/profile_routes.py
from flask import Blueprint, request
from ..controllers.profile_controller import ProfileController as c

profile_bp = Blueprint("profile", __name__, url_prefix="/api")

@profile_bp.get("/@me")
def me(): return c.me()

@profile_bp.put("/update_profile")
def update_profile(): return c.update_profile(request.get_json(force=True, silent=True) or {})

@profile_bp.get("/get_ClientProfile/<user_email>")
def get_client_profile(user_email): return c.get_client_profile(user_email)

@profile_bp.get("/get_ManagerProfile/<user_email>")
def get_manager_profile(user_email): return c.get_manager_profile(user_email)

@profile_bp.get("/pending_registrations")
def pending_registrations(): 
    return c.list_pending_registrations()

@profile_bp.post("/process_registrations")
def process_registrations():
    data = request.get_json(force=True) or {}
    return c.process_registrations(data.get("outcome"), data.get("email"))
