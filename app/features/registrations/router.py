# app/features/registrations/router.py
from fastapi import APIRouter, HTTPException
from app.features.registrations.schemas import RegistrationForm, OTPRequest, VerifyOTPRequest, VerifyRegistration
from app.features.registrations.service import generate_otp, send_otp_email, save_otp, verify_otp, insert_user, check_discord, insert_registration

router = APIRouter(prefix="/registration", tags=["Registrations"])

# -----------------------------
# 1. Soumission du formulaire -> envoie OTP
# -----------------------------
@router.get("/check-discord/{username}")
def check_discord_endpoint(username:str):

    return check_discord(username)

@router.post("/submit")
def submit_registration(form: RegistrationForm):
    try:
        otp = generate_otp()
        save_otp(form.email, otp)
        send_otp_email(form.email, otp)
        return {"message": "OTP envoyé par email"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# 2. Vérification OTP -> insertion user et role
# -----------------------------
@router.post("/verify-otp")
def verify_registration(data: VerifyRegistration):
    try:
        valid, msg = verify_otp(data.email, data.otp)
        if not valid:
            raise HTTPException(status_code=422, detail=msg)
        user_id = insert_user(data.form)
        insert_registration(user_id)
        return {"message": "Inscription validée", "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))