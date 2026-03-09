# app/features/registrations/router.py
from fastapi import APIRouter, HTTPException
from app.features.registrations.schemas import RegistrationForm,  VerifyRegistration, EmailRequest
from app.features.registrations.service import check_discord, insert_registration, check_registration_period
from app.features.emails.service import generate_otp, send_otp_email, save_otp, verify_otp
from app.features.members.service import  insert_user


router = APIRouter(prefix="/registration", tags=["Registrations"])

# -----------------------------
# 1. Soumission du formulaire -> envoie OTP
# -----------------------------
@router.get("/check-discord/{username}")
def check_discord_endpoint(username:str):

    return check_discord(username)

@router.post("/submit")
def submit_registration(data:  EmailRequest):
    try:
        otp = generate_otp()
        save_otp(data.email, otp)
        send_otp_email(data.email, otp)
        return {"message": "OTP envoyé par email"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-otp")
def verify_registration(data: VerifyRegistration):
    try:
        valid, msg = verify_otp(data.form.email, data.otp)
        if not valid:
            raise HTTPException(status_code=422, detail=msg)
        user_id = insert_user(data.form)
        insert_registration(user_id)
        return {"message": "Inscription validée", "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/form-status")
def get_registration_status():
    status, start, end, seconds_left = check_registration_period()
    
    if status == "no_event":
        raise HTTPException(status_code=404, detail="Aucun événement trouvé")
    
    if status == "not_open":
        return {
            "status": "not_open",
            "message": f"Le formulaire n'est pas encore ouvert. Il ouvrira le {start.strftime('%d/%m/%Y à %H:%M')}"
        }
    
    if status == "closed":
        return {
            "status": "closed",
            "message": f"Le formulaire est fermé depuis le {end.strftime('%d/%m/%Y à %H:%M')}"
        }
     
    days    = seconds_left // 86400
    hours   = (seconds_left % 86400) // 3600
    minutes = (seconds_left % 3600) // 60
    seconds = seconds_left % 60
    return {
        "status": "open",
        "message": "Le formulaire est ouvert",
        "countdown": {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": seconds_left
        }}

# Endpoints — Admin + Super Admin :
#
#   PAGE 1 — Formulaires soumis :
#     GET  /api/admin/events/{id}/registrations          → liste + filtres
#     GET  /api/admin/events/{id}/registrations/{uid}    → détail complet
#     PUT  /api/admin/events/{id}/registrations/{uid}/approve → approuver
#     PUT  /api/admin/events/{id}/registrations/{uid}/reject  → rejeter
#
#   PAGE 2 — Users acceptés :
#     GET  /api/admin/events/{id}/users                  → liste acceptés
#     POST /api/admin/events/{id}/users/send-emails      → envoyer emails
#     GET  /api/admin/events/{id}/users/export           → export Excel/CSV

from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.database import get_db
from app.features.registrations import service as reg_service
from app.dependencies import get_current_admin




@router.get(
    "/admin/events/{event_id}/registrations",
    summary="Liste des registrations"
)
def get_registrations(
    event_id: int,
    role:  Optional[str] = Query(None, description="PARTICIPANT, MENTOR ou STAFF"),
    state: Optional[str] = Query(None, description="APPROVED, REJECTED ou PENDING"),
    db=Depends(get_db),
    admin=Depends(get_current_admin)
):
    """
    Retourne toutes les registrations d'un événement.
    Défaut : tous les rôles, tous les statuts.

    Exemples :
      ?role=PARTICIPANT          → seulement les participants
      ?role=STAFF&state=PENDING  → staff en attente
      ?state=APPROVED            → tous les acceptés
    """
    return reg_service.get_registrations(db, event_id, role, state)


@router.get(
    "/admin/events/{event_id}/registrations/{user_id}",
    summary="Détail d'une registration"
)
def get_registration_detail(
    event_id: int,
    user_id:  int,
    db=Depends(get_db),
    admin=Depends(get_current_admin)
):
    """
    Retourne le détail complet d'une registration.
    Inclut toutes les infos du user + infos spécifiques à son rôle.
    """
    return reg_service.get_registration_detail(db, event_id, user_id)


@router.put(
    "/admin/events/{event_id}/registrations/{user_id}/approve",
    summary="Approuver une registration"
)
def approve_registration(
    event_id: int,
    user_id:  int,
    db=Depends(get_db),
    admin=Depends(get_current_admin)
):
    """
    Approuve une registration → STATE passe à APPROVED.
    """
    return reg_service.approve_registration(db, event_id, user_id)


@router.put(
    "/admin/events/{event_id}/registrations/{user_id}/reject",
    summary="Rejeter une registration"
)
def reject_registration(
    event_id: int,
    user_id:  int,
    db=Depends(get_db),
    admin=Depends(get_current_admin)
):
    """
    Rejette une registration → STATE passe à REJECTED.
    """
    return reg_service.reject_registration(db, event_id, user_id)


# USERS ACCEPTÉS 

@router.get(
    "/admin/events/{event_id}/users",
    summary="Liste des users acceptés"
)
def get_approved_users(
    event_id: int,
    role: Optional[str] = Query(None, description="PARTICIPANT, MENTOR ou STAFF"),
    db=Depends(get_db),
    admin=Depends(get_current_admin)
):
    """
    Retourne tous les users APPROUVÉS d'un événement.
    Filtrable par rôle.

    Exemples :
      (sans filtre)      → tous les acceptés
      ?role=PARTICIPANT  → seulement les participants acceptés
      ?role=MENTOR       → seulement les mentors acceptés
    """
    return reg_service.get_approved_users(db, event_id, role)



@router.get(
    "/admin/events/{event_id}/users/export",
    summary="Exporter les users en Excel ou CSV"
)
def export_users(
    event_id: int,
    role:   Optional[str] = Query(None, description="PARTICIPANT, MENTOR ou STAFF"),
    state:  Optional[str] = Query(None, description="APPROVED, REJECTED ou PENDING"),
    format: str           = Query("xlsx", description="xlsx ou csv"),
    db=Depends(get_db),
    admin=Depends(get_current_admin)
):
    """
    Exporte les users en fichier Excel ou CSV.
    Le fichier est téléchargé directement dans le navigateur.

    Exemples :
      ?format=xlsx                        → tous, format Excel
      ?role=PARTICIPANT&format=csv        → participants, format CSV
      ?state=APPROVED&format=xlsx         → acceptés, format Excel
      ?role=STAFF&state=PENDING&format=csv → staff en attente, CSV
    """
    return reg_service.export_users(db, event_id, role, state, format)