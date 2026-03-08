from app.database import get_cursor


# ── EVENT ────────────────────────────────────────────────────────

def get_all_events(db) -> list:
    """Retourne tous les événements triés du plus récent au plus ancien."""
    cursor = get_cursor(db)
    cursor.execute("SELECT * FROM EVENT ORDER BY START_REGISTRATION DESC")
    return cursor.fetchall()


def get_event_by_id(db, event_id: int) -> dict | None:
    """Retourne un événement par son ID, ou None si inexistant."""
    cursor = get_cursor(db)
    cursor.execute("SELECT * FROM EVENT WHERE ID_EVENT = %s", (event_id,))
    return cursor.fetchone()


def create_event(db, data: dict) -> int:
    """
    Insère un nouvel événement.
    data vient de EventCreate.model_dump() — clés en snake_case.
    start_registration → START_REGISTRATION (colonne DB)
    """
    cursor = get_cursor(db)
    cursor.execute(
        """
        INSERT INTO EVENT (START_REGISTRATION, END_REGISTRATION,
                           MAX_NBR_PARTICIPANT, MAX_NBR_MENTOR, MAX_NBR_STAFF)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            data["start_registration"],    # ✅ nom corrigé
            data["end_registration"],      # ✅ nom corrigé
            data["max_nbr_participant"],
            data["max_nbr_mentor"],
            data["max_nbr_staff"],
        )
    )
    db.commit()
    return cursor.lastrowid


def update_event(db, event_id: int, fields: dict) -> bool:
    """
    Met à jour seulement les champs envoyés.
    fields = {"START_REGISTRATION": ..., "MAX_NBR_PARTICIPANT": 50, ...}
    Construction dynamique du SET pour ne modifier que ce qui est fourni.
    """
    if not fields:
        return False

    set_clause = ", ".join(f"{col} = %s" for col in fields.keys())
    values     = list(fields.values()) + [event_id]

    cursor = get_cursor(db)
    cursor.execute(f"UPDATE EVENT SET {set_clause} WHERE ID_EVENT = %s", values)
    db.commit()
    return cursor.rowcount > 0


def delete_event(db, event_id: int) -> bool:
    """Supprime l'événement par son ID."""
    cursor = get_cursor(db)
    cursor.execute("DELETE FROM EVENT WHERE ID_EVENT = %s", (event_id,))
    db.commit()
    return cursor.rowcount > 0


# ── SHIFT ────────────────────────────────────────────────────────

def create_shift(db, shift: dict) -> int:
    """Insère un créneau dans SHIFT. Retourne son ID."""
    cursor = get_cursor(db)
    cursor.execute(
        "INSERT INTO SHIFT (DAY, START_TIME, END_TIME, SHIFT_TYPE) VALUES (%s, %s, %s, %s)",
        (shift["day"], shift["start_time"], shift["end_time"], shift["shift_type"])
    )
    db.commit()
    return cursor.lastrowid


def link_shift_to_event(db, event_id: int, shift_id: int):
    """Crée la liaison EVENT_SHIFT entre un événement et un créneau."""
    cursor = get_cursor(db)
    cursor.execute(
        "INSERT INTO EVENT_SHIFT (ID_EVENT, ID_SHIFT) VALUES (%s, %s)",
        (event_id, shift_id)
    )
    db.commit()


def get_shifts_by_event(db, event_id: int) -> list:
    """Retourne tous les créneaux d'un événement (staff + mentor)."""
    cursor = get_cursor(db)
    cursor.execute(
        """
        SELECT S.ID_SHIFT, S.DAY, S.START_TIME, S.END_TIME, S.SHIFT_TYPE
        FROM SHIFT S
        JOIN EVENT_SHIFT ES ON S.ID_SHIFT = ES.ID_SHIFT
        WHERE ES.ID_EVENT = %s
        ORDER BY S.DAY ASC, S.START_TIME ASC
        """,
        (event_id,)
    )
    return cursor.fetchall()


def get_shifts_by_event_and_type(db, event_id: int, shift_type: str) -> list:
    """Retourne les créneaux filtrés par type : STAFFING ou MENTORING."""
    cursor = get_cursor(db)
    cursor.execute(
        """
        SELECT S.ID_SHIFT, S.DAY, S.START_TIME, S.END_TIME, S.SHIFT_TYPE
        FROM SHIFT S
        JOIN EVENT_SHIFT ES ON S.ID_SHIFT = ES.ID_SHIFT
        WHERE ES.ID_EVENT = %s AND S.SHIFT_TYPE = %s
        ORDER BY S.DAY ASC, S.START_TIME ASC
        """,
        (event_id, shift_type)
    )
    return cursor.fetchall()


def delete_shifts_by_event(db, event_id: int):
    """
    Supprime tous les créneaux liés à un événement.
    Ordre obligatoire :
      1. Récupérer les IDs des shifts
      2. Supprimer les liaisons EVENT_SHIFT
      3. Supprimer les SHIFT eux-mêmes
    """
    cursor = get_cursor(db)

    cursor.execute("SELECT ID_SHIFT FROM EVENT_SHIFT WHERE ID_EVENT = %s", (event_id,))
    shift_ids = [row["ID_SHIFT"] for row in cursor.fetchall()]

    cursor.execute("DELETE FROM EVENT_SHIFT WHERE ID_EVENT = %s", (event_id,))

    for shift_id in shift_ids:
        cursor.execute("DELETE FROM SHIFT WHERE ID_SHIFT = %s", (shift_id,))

    db.commit()