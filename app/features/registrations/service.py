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


import io
import csv
import openpyxl
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from app.features.registrations import repository as reg_repo


# Colonnes communes à tous les rôles
COLUMNS_BASE = [
    "FIRST_NAME", "LAST_NAME", "EMAIL", "PHONE_NUMBER",
    "DISCORD_USERNAME", "UNIVERSITY", "FIELD_OF_STUDY",
    "ROLE", "STATE", "REGISTRATION_DATE"
]

# Colonnes spécifiques par rôle — ajoutées aux colonnes de base
COLUMNS_BY_ROLE = {
    "PARTICIPANT": COLUMNS_BASE + [
        "TEAM", "PROG_LANGUAGES", "MOTIVATION",
        "EXPECTATION", "MAIN_SKILLS", "SKILL_LEVEL"
    ],
    "MENTOR": COLUMNS_BASE + [
        "YEARS_OF_EXPERIENCE", "LINKEDIN", "PORTFOLIO",
        "AREA_OF_EXPERTISE", "TECHNOLOGIES", "MENTORED_BEFORE"
    ],
    "STAFF": COLUMNS_BASE + [
        "PREFERRED_ROLE", "ORGANIZED_BEFORE"
    ],
}


def get_registrations(db, event_id: int, role: str = None, state: str = None) -> list:
    """Retourne les registrations d'un événement. Filtrable par rôle et statut."""
    return reg_repo.get_registrations_by_event(db, event_id, role, state)


def get_registration_detail(db, event_id: int, user_id: int) -> dict:
    """
    Retourne le détail complet d'une registration.
    Ajoute les infos spécifiques au rôle selon le rôle du user.
    """
    reg = reg_repo.get_registration_detail(db, event_id, user_id)

    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration non trouvée pour user {user_id} / event {event_id}."
        )

    result = dict(reg)

    # Récupérer les infos spécifiques selon le rôle
    role = reg["ROLE"]
    if role == "PARTICIPANT":
        result["role_details"] = reg_repo.get_participant_details(db, user_id)
    elif role == "MENTOR":
        result["role_details"] = reg_repo.get_mentor_details(db, user_id)
    elif role == "STAFF":
        result["role_details"] = reg_repo.get_staff_details(db, user_id)
    else:
        result["role_details"] = None

    return result


def approve_registration(db, event_id: int, user_id: int) -> dict:
    #Approuve une registration
    reg = reg_repo.get_registration_detail(db, event_id, user_id)
    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration non trouvée.")

    if reg["STATE"] == "APPROVED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Déjà approuvée.")

    reg_repo.update_registration_state(db, event_id, user_id, "APPROVED")
    return {"message": f"Registration de {reg['FIRST_NAME']} {reg['LAST_NAME']} approuvée."}


def reject_registration(db, event_id: int, user_id: int) -> dict:
    #Rejette une registration
    reg = reg_repo.get_registration_detail(db, event_id, user_id)
    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration non trouvée.")

    if reg["STATE"] == "REJECTED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Déjà rejetée.")

    reg_repo.update_registration_state(db, event_id, user_id, "REJECTED")
    return {"message": f"Registration de {reg['FIRST_NAME']} {reg['LAST_NAME']} rejetée."}


def get_approved_users(db, event_id: int, role: str = None) -> list:
    #Retourne les users acceptés. Filtrable par rôle
    return reg_repo.get_approved_users(db, event_id, role)




def export_users(db, event_id: int, role: str = None, state: str = None, format: str = "xlsx"):
    """
    Exporte les users en Excel ou CSV.
    Les colonnes s'adaptent au rôle :
      - PARTICIPANT → colonnes base + colonnes participant
      - MENTOR      → colonnes base + colonnes mentor
      - STAFF       → colonnes base + colonnes staff
      - Sans rôle   → colonnes base seulement (tous rôles)
    """
    users = reg_repo.get_users_for_export(db, event_id, role, state)

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun user trouvé avec ces filtres."
        )

    # Choisir les colonnes selon le rôle
    role_upper = role.upper() if role else None
    columns    = COLUMNS_BY_ROLE.get(role_upper, COLUMNS_BASE)

    # Nom du fichier
    role_part  = f"_{role.lower()}" if role else "_all"
    state_part = f"_{state.lower()}" if state else "_all_status"
    filename   = f"event_{event_id}_users{role_part}{state_part}.{format}"

    if format == "xlsx":
        # ── Export Excel ─────────────────────────────────────────
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Users"

        # En-têtes
        ws.append(columns)

        # Données — convertir en string pour éviter les erreurs de type
        for user in users:
            ws.append([str(user.get(col, "")) for col in columns])

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    else:
        # ── Export CSV ───────────────────────────────────────────
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows([{k: str(v) for k, v in user.items()} for user in users])
        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )