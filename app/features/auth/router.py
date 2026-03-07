# ================================================================
# app/features/auth/router.py
# ================================================================

from fastapi import APIRouter, Depends
from app.database import get_db
from app.features.auth.schemas import LoginRequest, LoginResponse, AdminCreate
from app.features.auth import service as auth_service
from app.dependencies import get_current_admin, get_super_admin

router = APIRouter()


# ── ENDPOINT PUBLIC ───────────────────────────────────────────────

@router.post(
    "/auth/login",
    response_model=LoginResponse,
    summary="Connexion admin"
)
def login(request: LoginRequest, db=Depends(get_db)):
    """
    Login admin → retourne JWT token.
    Body: { "email": "...", "password": "..." }
    """
    return auth_service.login_admin(db, request.email, request.password)


# ── ENDPOINT ADMIN (tout admin connecté) ─────────────────────────

@router.get(
    "/auth/me",
    summary="Admin connecté"
)
def get_me(admin: dict = Depends(get_current_admin)):
    """
    Retourne les infos de l'admin connecté.
    Requiert : Authorization: Bearer <token>
    """
    return {"email": admin["email"], "role": admin["role"]}


# ── ENDPOINTS SUPER ADMIN UNIQUEMENT ─────────────────────────────

@router.get(
    "/admin/admins",
    summary="Liste tous les admins",
    description="Réservé au Super Admin."
)
def get_all_admins(
    db=Depends(get_db),
    super_admin=Depends(get_super_admin)   # ← bloque si pas super_admin
):
    """
    Retourne la liste de tous les admins.
    PASSWORD_HASH jamais retourné.
    """
    from app.features.auth import repository as auth_repo
    return auth_repo.get_all_admins(db)


@router.post(
    "/admin/admins",
    summary="Créer un admin",
    description="Réservé au Super Admin."
)
def create_admin(
    data: AdminCreate,
    db=Depends(get_db),
    super_admin=Depends(get_super_admin)
):
    """
    Crée un nouvel admin.
    Body: { "email": "...", "password": "...", "role": "ADMIN" }
    """
    return auth_service.create_admin(db, data.email, data.password, data.role)


@router.delete(
    "/admin/admins/{admin_id}",
    summary="Supprimer un admin",
    description="Réservé au Super Admin. Ne peut pas se supprimer soi-même."
)
def delete_admin(
    admin_id: int,
    db=Depends(get_db),
    super_admin=Depends(get_super_admin)
):
    """
    Supprime un admin par son ID.
    Le Super Admin ne peut pas supprimer son propre compte.
    """
    return auth_service.delete_admin(db, admin_id, super_admin["email"])