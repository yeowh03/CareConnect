"""User Lookup Service for CareConnect Backend.

This module provides utility functions for finding and retrieving
user, client, and manager records from the database.
"""

from ..models import User, Client, Manager
from flask import session
from ..extensions import db

def get_current_user():
    """Get the currently authenticated user from session.
    
    Returns:
        User: Current user instance or None if not authenticated.
    """
    email = session.get("user_email")
    if not email:
        return None
    return db.session.get(User, email)

def find_user_by_email(email):
    """Find user by email address.
    
    Args:
        email (str): User's email address.
        
    Returns:
        User: User instance or None if not found.
    """
    return User.query.get(email)

def find_client_by_email(email):
    """Find client by email address.
    
    Args:
        email (str): Client's email address.
        
    Returns:
        Client: Client instance or None if not found.
    """
    return Client.query.get(email)

def find_manager_by_email(email):
    """Find manager by email address.
    
    Args:
        email (str): Manager's email address.
        
    Returns:
        Manager: Manager instance or None if not found.
    """
    return Manager.query.get(email)

def find_managers_by_cc(cc: str):
    """Find manager by community club name.
    
    Args:
        cc (str): Community club name.
        
    Returns:
        Manager: First manager for the CC or None if not found.
    """
    return Manager.query.filter_by(cc=cc).first()