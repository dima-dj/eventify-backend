# app/features/registrations/service.py
import random
from datetime import datetime, timedelta, date
from app.database import get_db_connection
import smtplib
from email.message import EmailMessage
from app.config import settings

OTP_EXPIRATION_MINUTES = 5


def check_discord(username):

    conn = get_db_connection()
    try:
       cursor = conn.cursor(dictionary=True)

       query = """
    SELECT * FROM CLUB_MEMBERS
    WHERE DISCORD_USERNAME = %s
    """

       cursor.execute(query,(username,))
       member = cursor.fetchone()

       if member:
           roles = ["PARTICIPANT","MENTOR","STAFF"]
       else:
           roles = ["PARTICIPANT"]

       return {
        "club_member": member is not None,
        "roles": roles
    }
    finally:
        if conn.is_connected():
            conn.close()


def generate_otp():
    return f"{random.randint(100000, 999999)}"

def send_otp_email(email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Your OTP code Eventify"
    msg["From"] = "noreply@eventify.com"
    msg["To"] = email
    msg.set_content(f"Your verification code is : {otp}")

    # SMTP réel (exemple Gmail)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
       server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
       server.send_message(msg)
    
    

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

# -----------------------------
# Insert user et role
# -----------------------------
def insert_user(form_data):
    conn = get_db_connection()
    try:
       cursor = conn.cursor()

    # USERS
       cursor.execute("""
        INSERT INTO USERS 
        (FIRST_NAME,LAST_NAME,EMAIL,PHONE_NUMBER,DISCORD_USERNAME,UNIVERSITY,FIELD_OF_STUDY,ROLE)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        form_data.first_name,
        form_data.last_name,
        form_data.email,
        form_data.phone_number,
        form_data.discord_username,
        form_data.university,
        form_data.field_of_study,
        form_data.role
    ))
       user_id = cursor.lastrowid

    # ROLE TABLE
       if form_data.role == "PARTICIPANT":
           cursor.execute("""
            INSERT INTO PARTICIPANT 
            (ID_USER, TEAM, PROG_LANGUAGES, MOTIVATION, EXPECTATION, MAIN_SKILLS, SKILL_LEVEL)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id,
            form_data.team,
            form_data.prog_languages,
            form_data.motivation,
            form_data.expectation,
            form_data.main_skills,
            form_data.skill_level
        ))
       elif form_data.role == "MENTOR":
        cursor.execute("""
            INSERT INTO MENTOR 
            (ID_USER, YEARS_OF_EXPERIENCE, LINKEDIN, PORTFOLIO, AREA_OF_EXPERTISE, TECHNOLOGIES, MENTORED_BEFORE)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id,
            form_data.years_of_experience,
            form_data.linkedin,
            form_data.portfolio,
            form_data.area_of_expertise,
            form_data.technologies,
            form_data.mentored_before
        ))
       elif form_data.role == "STAFF":
        cursor.execute("""
            INSERT INTO STAFF 
            (ID_USER, PREFERRED_ROLE, ORGANIZED_BEFORE)
            VALUES (%s,%s,%s)
        """, (
            user_id,
            form_data.preferred_role,
            form_data.organized_before
        ))

       conn.commit()
    
       return user_id
    finally:
        if conn.is_connected():
            conn.close()



def insert_registration(user_id):
    conn = get_db_connection()  # connexion à la base
    try:
        cursor = conn.cursor()

        # Récupérer le dernier ID_EVENT inséré
        cursor.execute("SELECT ID_EVENT FROM EVENT ORDER BY ID_EVENT DESC LIMIT 1")
        result = cursor.fetchone()
        if not result:
            raise ValueError("Aucun événement trouvé dans la table EVENT")
        last_event_id = result[0]

        # Requête pour insérer la registration
        query = """
        INSERT INTO REGISTRATION (ID_EVENT, ID_USER, REGISTRATION_DATE)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (last_event_id, user_id, date.today()))
        conn.commit()
        return True

    finally:
        if conn.is_connected():
            conn.close()

def check_registration_period():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT START_REGISTRATION, END_REGISTRATION FROM EVENT ORDER BY ID_EVENT DESC LIMIT 1")
        event = cursor.fetchone()
        
        if not event:
            return "no_event", None, None, None
        
        now = datetime.now()
        start = event["START_REGISTRATION"]
        end = event["END_REGISTRATION"]
        
        if now < start:
            return "not_open", start, end, None
        elif now > end:
            return "closed", start, end, None
        else:
            seconds_left = int((end - now).total_seconds())
            return "open", start, end, seconds_left
    finally:
        if conn.is_connected():
            conn.close()