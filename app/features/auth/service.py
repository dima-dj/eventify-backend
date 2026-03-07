# ================================================================
# app/features/auth/service.py
# ================================================================
# RÔLE : logique métier du module auth
# RÈGLE : pas de SQL ici — on appelle repository.py pour ça
# APPELÉ PAR : router.py
# APPELLE : repository.py + security.py
# ================================================================

from fastapi import HTTPException, status
from app.features.auth import repository as auth_repo
from app.features.auth.schemas import LoginResponse
from app.utils.security import verify_password, create_access_token, hash_password


def login_admin(db, email: str, password: str) -> LoginResponse:
    """
    Authentifie un admin :
    1. Cherche l'admin en DB par email
    2. Vérifie le mot de passe avec bcrypt
    3. Crée et retourne un token JWT
    """
    # chercher l'admin en DB
    admin = auth_repo.get_admin_by_email(db, email)

    # if email inexistant
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect."
        )

    # compare le mot de passe saisi avec le hash bcrypt en DB
    if not verify_password(password, admin["PASSWORD_HASH"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect."
        )

    # créer le token JWT
    token = create_access_token(
        email=admin["EMAIL"],
        role=admin["ROLE_ADMIN"]   # "ADMIN" ou "SUPER_ADMIN"
    )

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        role=admin["ROLE_ADMIN"],
        email=admin["EMAIL"]
    )


def create_admin(db, email: str, password: str, role: str) -> dict:
    """
    Crée un nouvel admin :
    1. Vérifie que l'email n'existe pas déjà en DB
    2. Valide que le rôle est ADMIN ou SUPER_ADMIN
    3. Hash le mot de passe avec bcrypt avant insertion
    4. Insère en DB et retourne les infos du nouvel admin
    """
    # vérifier que l'email n'est pas déjà pris
    existing = auth_repo.get_admin_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un admin avec cet email existe déjà."
        )

    # valider le rôle (seulement ces deux valeurs acceptées)
    if role not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rôle invalide. Valeurs acceptées : ADMIN, SUPER_ADMIN"
        )

    # hasher le mot de passe 
    password_hash = hash_password(password)

    # insérer en DB
    new_id = auth_repo.create_admin(db, email, password_hash, role)

    return {
        "id_admin": new_id,
        "email":    email,
        "role":     role,
        "message":  "Admin créé avec succès."
    }


def delete_admin(db, admin_id: int, current_admin_email: str) -> dict:
    """
    Supprime un admin :
    1. Vérifie que l'admin cible existe en DB
    2. Empêche le Super Admin de se supprimer lui-même
    3. Supprime et retourne un message de confirmation
    """
    # récupérer tous les admins et trouver la cible
    admins = auth_repo.get_all_admins(db)
    target = next((a for a in admins if a["ID_ADMIN"] == admin_id), None)

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin non trouvé."
        )

    # bloquer l'auto-suppression
    if target["EMAIL"].lower() == current_admin_email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte."
        )

    # supprimer
    auth_repo.delete_admin(db, admin_id)
    return {"message": f"Admin {target['EMAIL']} supprimé avec succès."}