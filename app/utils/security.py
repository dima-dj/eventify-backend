# Deux responsabilités :
#   1. Hash / vérification des mots de passe avec bcrypt
#   2. Création / décodage des tokens JWT


import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from app.config import settings



def hash_password(plain_password: str) -> str:
    #Hash un mot de passe avec bcrypt.

    password_bytes = plain_password.encode("utf-8")   # str → bytes
    salt           = bcrypt.gensalt(rounds=12)         # salt aléatoire
    hashed         = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")                      # bytes → str pour DB


def verify_password(plain_password: str, hashed_password: str) -> bool:
    #Vérifie si un mot de passe correspond à son hash en DB.
    
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )




def create_access_token(email: str, role: str) -> str:
    #Crée un JWT token signé pour un admin.

    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)

    payload = {
        "sub":  email,   # identifiant de l'admin
        "role": role,    # 'admin' ou 'super_admin'
        "exp":  expire,  # expiration automatique
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(token: str) -> dict:
    #Décode et vérifie un JWT token.

    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )