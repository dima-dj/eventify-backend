import bcrypt

def hash_password(plain: str) -> str:
    """Hash un mot de passe avec bcrypt."""
    pw_bytes = plain.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pw_bytes, salt).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    """Vérifie si un mot de passe correspond à son hash."""
    return bcrypt.checkpw(
        plain.encode('utf-8'),
        hashed.encode('utf-8')
    )