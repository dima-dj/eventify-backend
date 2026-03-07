# ================================================================
# app/features/auth/schemas.py
# ================================================================

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type:   str
    role:         str
    email:        str


class AdminCreate(BaseModel):
    """
    Ce que le Super Admin envoie pour créer un nouvel admin.
    POST /api/admin/admins
    """
    email:      EmailStr
    password:   str
    role:       str = "ADMIN"   # ADMIN par défaut, Super Admin peut mettre SUPER_ADMIN


class AdminResponse(BaseModel):
    """
    Ce que l'API retourne quand on liste les admins.
    Le PASSWORD_HASH n'est JAMAIS retourné.
    """
    id_admin:   int
    email:      str
    role:       str