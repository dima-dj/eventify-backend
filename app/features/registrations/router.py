# app/features/registrations/router.py
from fastapi import APIRouter, HTTPException
from app.features.registrations.schemas import RegistrationForm,  VerifyRegistration, EmailRequest
from app.features.registrations.service import generate_otp, send_otp_email, save_otp, verify_otp, insert_user, check_discord, insert_registration, check_registration_period

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