from ..models import User, Client, Manager
from flask import session
from ..extensions import db

# ---------- user helpers ----------
def get_current_user():
    email = session.get("user_email")
    if not email:
        return None
    return db.session.get(User, email)

def find_user_by_email(email): return User.query.get(email)
def find_client_by_email(email): return Client.query.get(email)
def find_manager_by_email(email): return Manager.query.get(email)

def find_managers_by_cc(cc: str):
    return Manager.query.filter_by(cc=cc).first()