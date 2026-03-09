from app.database import get_cursor


def get_registrations_by_event(db, event_id: int, role: str = None, state: str = None) -> list:
    """
    Retourne toutes les registrations d'un événement.
    return :first_name, last_name, registration_date, state.
    Filtres optionnels : role et state.
    """
    cursor = get_cursor(db)

    query = """
        SELECT R.ID_USER, R.ID_EVENT, R.REGISTRATION_DATE, R.STATE,
               U.FIRST_NAME, U.LAST_NAME
        FROM REGISTRATION R
        JOIN USERS U ON R.ID_USER = U.ID_USER
        WHERE R.ID_EVENT = %s
    """
    params = [event_id]

    if role:
        query += " AND U.ROLE = %s"
        params.append(role.upper())

    if state:
        query += " AND R.STATE = %s"
        params.append(state.upper())

    query += " ORDER BY R.REGISTRATION_DATE DESC"

    cursor.execute(query, params)
    return cursor.fetchall()


def get_registration_detail(db, event_id: int, user_id: int) -> dict | None:
    """
    Retourne les infos complètes d'une registration.
    """
    cursor = get_cursor(db)
    cursor.execute(
        """
        SELECT R.ID_EVENT, R.ID_USER, R.REGISTRATION_DATE, R.STATE,
               U.FIRST_NAME, U.LAST_NAME, U.EMAIL, U.PHONE_NUMBER,
               U.DISCORD_USERNAME, U.UNIVERSITY, U.FIELD_OF_STUDY, U.ROLE
        FROM REGISTRATION R
        JOIN USERS U ON R.ID_USER = U.ID_USER
        WHERE R.ID_EVENT = %s AND R.ID_USER = %s
        """,
        (event_id, user_id)
    )
    return cursor.fetchone()


def get_participant_details(db, user_id: int) -> dict | None:
    """Retourne les infos spécifiques d'un participant."""
    cursor = get_cursor(db)
    cursor.execute("SELECT * FROM PARTICIPANT WHERE ID_USER = %s", (user_id,))
    return cursor.fetchone()


def get_mentor_details(db, user_id: int) -> dict | None:
    """Retourne les infos spécifiques d'un mentor."""
    cursor = get_cursor(db)
    cursor.execute("SELECT * FROM MENTOR WHERE ID_USER = %s", (user_id,))
    return cursor.fetchone()


def get_staff_details(db, user_id: int) -> dict | None:
    """Retourne les infos spécifiques d'un staff."""
    cursor = get_cursor(db)
    cursor.execute("SELECT * FROM STAFF WHERE ID_USER = %s", (user_id,))
    return cursor.fetchone()



def update_registration_state(db, event_id: int, user_id: int, state: str) -> bool:
    """
    Met à jour le statut d'une registration.
    state = 'APPROVED' ou 'REJECTED'
    """
    cursor = get_cursor(db)
    cursor.execute(
        "UPDATE REGISTRATION SET STATE = %s WHERE ID_EVENT = %s AND ID_USER = %s",
        (state, event_id, user_id)
    )
    db.commit()
    return cursor.rowcount > 0


#USERS ACCEPTÉS 

def get_approved_users(db, event_id: int, role: str = None) -> list:
    """
    Retourne les users APPROUVÉS d'un événement.
    return : first_name, last_name, role seulement.
    """
    cursor = get_cursor(db)

    query = """
        SELECT R.ID_USER, R.ID_EVENT,
               U.FIRST_NAME, U.LAST_NAME, U.ROLE
        FROM REGISTRATION R
        JOIN USERS U ON R.ID_USER = U.ID_USER
        WHERE R.ID_EVENT = %s AND R.STATE = 'APPROVED'
    """
    params = [event_id]

    if role:
        query += " AND U.ROLE = %s"
        params.append(role.upper())

    query += " ORDER BY U.LAST_NAME ASC"

    cursor.execute(query, params)
    return cursor.fetchall()


#EXPORT

def get_users_for_export(db, event_id: int, role: str = None, state: str = None) -> list:
    """
    Retourne les users pour l'export avec infos spécifiques au rôle.

    Si role = PARTICIPANT → JOIN PARTICIPANT pour toutes ses colonnes
    Si role = MENTOR      → JOIN MENTOR pour toutes ses colonnes
    Si role = STAFF       → JOIN STAFF pour toutes ses colonnes
    Si role absent        → colonnes communes seulement (tous rôles confondus)

    Filtrable par statut dans tous les cas.
    """
    cursor = get_cursor(db)
    params = [event_id]

    if role == "PARTICIPANT":
        query = """
            SELECT U.FIRST_NAME, U.LAST_NAME, U.EMAIL, U.PHONE_NUMBER,
                   U.DISCORD_USERNAME, U.UNIVERSITY, U.FIELD_OF_STUDY,
                   U.ROLE, R.STATE, R.REGISTRATION_DATE,
                   P.TEAM, P.PROG_LANGUAGES, P.MOTIVATION,
                   P.EXPECTATION, P.MAIN_SKILLS, P.SKILL_LEVEL
            FROM REGISTRATION R
            JOIN USERS U ON R.ID_USER = U.ID_USER
            JOIN PARTICIPANT P ON U.ID_USER = P.ID_USER
            WHERE R.ID_EVENT = %s
        """

    elif role == "MENTOR":
        query = """
            SELECT U.FIRST_NAME, U.LAST_NAME, U.EMAIL, U.PHONE_NUMBER,
                   U.DISCORD_USERNAME, U.UNIVERSITY, U.FIELD_OF_STUDY,
                   U.ROLE, R.STATE, R.REGISTRATION_DATE,
                   M.YEARS_OF_EXPERIENCE, M.LINKEDIN, M.PORTFOLIO,
                   M.AREA_OF_EXPERTISE, M.TECHNOLOGIES, M.MENTORED_BEFORE
            FROM REGISTRATION R
            JOIN USERS U ON R.ID_USER = U.ID_USER
            JOIN MENTOR M ON U.ID_USER = M.ID_USER
            WHERE R.ID_EVENT = %s
        """

    elif role == "STAFF":
        query = """
            SELECT U.FIRST_NAME, U.LAST_NAME, U.EMAIL, U.PHONE_NUMBER,
                   U.DISCORD_USERNAME, U.UNIVERSITY, U.FIELD_OF_STUDY,
                   U.ROLE, R.STATE, R.REGISTRATION_DATE,
                   S.PREFERRED_ROLE, S.ORGANIZED_BEFORE
            FROM REGISTRATION R
            JOIN USERS U ON R.ID_USER = U.ID_USER
            JOIN STAFF S ON U.ID_USER = S.ID_USER
            WHERE R.ID_EVENT = %s
        """

    else:
        # Tous rôles → colonnes communes seulement
        query = """
            SELECT U.FIRST_NAME, U.LAST_NAME, U.EMAIL, U.PHONE_NUMBER,
                   U.DISCORD_USERNAME, U.UNIVERSITY, U.FIELD_OF_STUDY,
                   U.ROLE, R.STATE, R.REGISTRATION_DATE
            FROM REGISTRATION R
            JOIN USERS U ON R.ID_USER = U.ID_USER
            WHERE R.ID_EVENT = %s
        """

    # Filtre statut — s'applique à tous les cas
    if state:
        query += " AND R.STATE = %s"
        params.append(state.upper())

    query += " ORDER BY U.ROLE ASC, U.LAST_NAME ASC"

    cursor.execute(query, params)
    return cursor.fetchall()
