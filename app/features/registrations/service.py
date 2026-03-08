# app/features/registrations/service.py

from datetime import datetime, timedelta, date
from app.database import get_db_connection



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