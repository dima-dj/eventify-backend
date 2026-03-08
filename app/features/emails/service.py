import random
import smtplib
from app.database import get_db_connection
from email.message import EmailMessage
from app.config import settings
from datetime import datetime, timedelta, date

OTP_EXPIRATION_MINUTES = 5


def verify_otp(email: str, otp: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM OTP_TEMP WHERE EMAIL=%s", (email,))
        row = cursor.fetchone()
        if not row:
            return False, "OTP non trouvé"       # no manual close, finally handles it
        if row["otp"] != otp:
            return False, "OTP invalide"          # no manual close
        if row["expiration"] < datetime.now():
            return False, "OTP expiré"            # no manual close
        cursor.execute("DELETE FROM OTP_TEMP WHERE EMAIL=%s", (email,))
        conn.commit()
        return True, "OTP valide"
    finally:
        if conn and conn.is_connected():
            conn.close()                          # only ONE place that closes


def save_otp(email: str, otp: str):
    conn = get_db_connection()
    try:
       cursor = conn.cursor()
       expiration = datetime.now() + timedelta(minutes=OTP_EXPIRATION_MINUTES)
       cursor.execute("""
        INSERT INTO OTP_TEMP (EMAIL, OTP, EXPIRATION)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE OTP=%s, EXPIRATION=%s
    """, (email, otp, expiration, otp, expiration))
       conn.commit()
    finally:
        if conn.is_connected():
            conn.close()

def generate_otp():
    return f"{random.randint(100000, 999999)}"

def send_otp_email(email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Your OTP code Eventify"
    msg["From"] = settings.SMTP_USER
    msg["To"] = email
    msg.set_content(f"Your verification code is : {otp}")

    # SMTP réel (exemple Gmail)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
       server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
       server.send_message(msg)
    
    
