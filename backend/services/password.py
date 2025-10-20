from passlib.hash import argon2

# ---------- password helpers ----------
def hash_password(pw: str) -> str:
    return argon2.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    from passlib.hash import argon2 as _argon
    return _argon.verify(pw, hashed)