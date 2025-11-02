"""Password Hashing Service for CareConnect Backend.

This module provides secure password hashing and verification
using the Argon2 algorithm for user authentication.
"""

from passlib.hash import argon2

def hash_password(pw: str) -> str:
    """Hash a password using Argon2.
    
    Args:
        pw (str): Plain text password to hash.
        
    Returns:
        str: Hashed password string.
    """
    return argon2.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    """Verify a password against its hash.
    
    Args:
        pw (str): Plain text password to verify.
        hashed (str): Hashed password to compare against.
        
    Returns:
        bool: True if password matches, False otherwise.
    """
    from passlib.hash import argon2 as _argon
    return _argon.verify(pw, hashed)