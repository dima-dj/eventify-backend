# ================================================================
# app/features/events/service.py
# ================================================================
# RÔLE : logique métier des événements
# RÈGLE : pas de SQL ici — on appelle repository.py
# APPELÉ PAR : router.py
# APPELLE : repository.py
# ================================================================

from fastapi import HTTPException, status
from app.features.event import repository as event_repo


def get_all_events(db) -> list:
    """Retourne tous les événements avec leurs créneaux."""
    events = event_repo.get_all_events(db)
    for event in events:
        event["shifts"] = event_repo.get_shifts_by_event(db, event["ID_EVENT"])
    return events


def get_event_by_id(db, event_id: int) -> dict:
    """Retourne un événement avec ses créneaux. Lève 404 si inexistant."""
    event = event_repo.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Événement {event_id} non trouvé."
        )
    event["shifts"] = event_repo.get_shifts_by_event(db, event_id)
    return event


def create_event(db, data) -> dict:
    """
    Crée un événement complet :
    1. Insère dans EVENT → récupère ID_EVENT
    2. Pour chaque shift : insère dans SHIFT → récupère ID_SHIFT
    3. Crée la liaison dans EVENT_SHIFT
    """
    event_dict = data.model_dump(mode="json")
    shifts     = event_dict.pop("shifts", [])

    event_id = event_repo.create_event(db, event_dict)

    for shift in shifts:
        shift_id = event_repo.create_shift(db, shift)
        event_repo.link_shift_to_event(db, event_id, shift_id)

    return {
        "id_event": event_id,
        "message":  f"Événement créé avec {len(shifts)} créneau(x)."
    }


def update_event(db, event_id: int, data) -> dict:
    """
    ✅ NOUVELLE APPROCHE — data contient tout : infos event + shifts
    Met à jour un événement :
    1. Vérifie que l'événement existe
    2. Met à jour les champs infos (seulement ceux envoyés, non-None)
    3. Si shifts fourni dans le body → supprime les anciens et recrée les nouveaux
       Si shifts absent (None)       → les shifts existants ne changent pas
    """
    print("DEBUG type de data:", type(data))
    print("DEBUG fields de EventUpdate:", list(data.model_fields.keys()))
    
    # Étape 1 — vérifier que l'événement existe
    existing = event_repo.get_event_by_id(db, event_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Événement {event_id} non trouvé."
        )

    # Étape 2 — extraire les shifts du body AVANT de traiter les infos event
    # model_dump(mode="json") convertit Enum → string, datetime → string
    update_data = data.model_dump(mode="json", exclude_none=True)
    print("DEBUG update_data:", update_data)        # ← ajoute ça
    new_shifts  = update_data.pop("shifts", None)
    print("DEBUG new_shifts:", new_shifts)          # ← et ça
    # Mapper les noms Pydantic (snake_case) → noms DB (UPPERCASE)
    field_mapping = {
        "start_registration":  "START_REGISTRATION",
        "end_registration":    "END_REGISTRATION",
        "max_nbr_participant": "MAX_NBR_PARTICIPANT",
        "max_nbr_mentor":      "MAX_NBR_MENTOR",
        "max_nbr_staff":       "MAX_NBR_STAFF",
    }
    db_fields = {field_mapping[k]: v for k, v in update_data.items() if k in field_mapping}

    if db_fields:
        event_repo.update_event(db, event_id, db_fields)

    # Étape 3 — remplacer les shifts seulement si fournis dans le body
    # new_shifts = None  → rien ne change
    # new_shifts = []    → supprime tous les shifts sans en recréer
    # new_shifts = [...]  → supprime les anciens et crée les nouveaux
    if new_shifts is not None:
        event_repo.delete_shifts_by_event(db, event_id)   # supprime les anciens
        for shift in new_shifts:
            shift_id = event_repo.create_shift(db, shift)
            event_repo.link_shift_to_event(db, event_id, shift_id)

    return {"message": "Événement mis à jour avec succès."}


def delete_event(db, event_id: int) -> dict:
    """
    Supprime un événement et tous ses créneaux.
    Ordre : shifts d'abord → événement ensuite (contrainte FK).
    """
    existing = event_repo.get_event_by_id(db, event_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Événement {event_id} non trouvé."
        )

    event_repo.delete_shifts_by_event(db, event_id)
    event_repo.delete_event(db, event_id)

    return {"message": f"Événement {event_id} et tous ses créneaux supprimés."}


def get_event_shifts(db, event_id: int, shift_type: str = None) -> list:
    """
    Retourne les créneaux d'un événement.
    shift_type = 'STAFFING' ou 'MENTORING' → filtre par type.
    Sans shift_type → tous les créneaux.
    """
    existing = event_repo.get_event_by_id(db, event_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Événement {event_id} non trouvé."
        )

    if shift_type:
        return event_repo.get_shifts_by_event_and_type(db, event_id, shift_type.upper())

    return event_repo.get_shifts_by_event(db, event_id)