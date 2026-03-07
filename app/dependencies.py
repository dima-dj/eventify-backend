from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.utils.security import decode_access_token

# Indique à FastAPI où chercher le token (header Authorization: Bearer ...)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_admin(token: str = Depends(oauth2_scheme)) -> dict:
    #Vérifie que le token JWT est valide et non expiré.
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré. Veuillez vous reconnecter.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)    # décode le JWT

        email: str = payload.get("sub")         # "sub" = identifiant dans JWT
        role:  str = payload.get("role")

        if email is None or role is None:
            raise credentials_exception

        return {"email": email, "role": role.upper()}   # toujours UPPERCASE

    except JWTError:
        # Token invalide, expiré ou signature incorrecte
        raise credentials_exception


def get_super_admin(admin: dict = Depends(get_current_admin)) -> dict:
    #Vérifie en plus que le role est SUPER_ADMIN.
    #Si role == "ADMIN" → 403 Forbidden
    #Si role == "SUPER_ADMIN" → OK, retourne le même dict

    if admin["role"].upper() != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé au Super Admin."
        )
    return admin