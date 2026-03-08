# Endpoints :
#   PUBLIC (formulaire d'inscription) :
#     GET  /api/events/{id}/shifts/staff    → créneaux STAFFING
#     GET  /api/events/{id}/shifts/mentors  → créneaux MENTORING
#
#   SUPER ADMIN seulement :
#     GET    /api/admin/events              → liste tous les événements
#     GET    /api/admin/events/{id}         → détail un événement
#     POST   /api/admin/events              → créer événement + shifts
#     PUT    /api/admin/events/{id}         → modifier événement + shifts
#     DELETE /api/admin/events/{id}         → supprimer tout

from fastapi import APIRouter, Depends
from app.database import get_db
from app.features.event.schemas import EventCreate, EventUpdate
from app.features.event import service as event_service
from app.dependencies import get_super_admin

router = APIRouter()


# ── ENDPOINTS PUBLICS — utilisés dans le formulaire d'inscription ─

@router.get(
    "/events/{event_id}/shifts/staff",
    summary="Créneaux staff d'un événement"
)
def get_staff_shifts(event_id: int, db=Depends(get_db)):
    """
    Retourne tous les créneaux STAFFING d'un événement.
    Affiché dans le formulaire quand le rôle sélectionné = STAFF.
    Le staff choisit parmi ces créneaux ceux qui l'arrangent.
    """
    return event_service.get_event_shifts(db, event_id, shift_type="STAFFING")


@router.get(
    "/events/{event_id}/shifts/mentors",
    summary="Créneaux mentor d'un événement"
)
def get_mentor_shifts(event_id: int, db=Depends(get_db)):
    """
    Retourne tous les créneaux MENTORING d'un événement.
    Affiché dans le formulaire quand le rôle sélectionné = MENTOR.
    Le mentor choisit parmi ces créneaux ceux qui l'arrangent.
    """
    return event_service.get_event_shifts(db, event_id, shift_type="MENTORING")


# ── ENDPOINTS SUPER ADMIN ─────────────────────────────────────────

@router.get(
    "/admin/events",
    summary="Liste tous les événements"
)
def get_all_events(db=Depends(get_db), super_admin=Depends(get_super_admin)):
    """Retourne tous les événements avec leurs créneaux."""
    return event_service.get_all_events(db)


@router.get(
    "/admin/events/{event_id}",
    summary="Détail d'un événement"
)
def get_event(
    event_id: int,
    db=Depends(get_db),
    super_admin=Depends(get_super_admin)
):
    """Retourne un événement avec tous ses créneaux staff et mentor."""
    return event_service.get_event_by_id(db, event_id)


@router.post(
    "/admin/events",
    summary="Créer un événement",
    status_code=201
)
def create_event(
    data: EventCreate,
    db=Depends(get_db),
    super_admin=Depends(get_super_admin)
):
    """
    Crée un événement avec tous ses créneaux staff et mentor.

    Body exemple :
    {
        "start_registration": "2026-04-01T08:00:00",
        "end_registration":   "2026-04-10T23:59:00",
        "max_nbr_participant": 100,
        "max_nbr_mentor": 10,
        "max_nbr_staff": 20,
        "shifts": [
            { "day": "2026-04-14", "start_time": "09:00:00",
              "end_time": "12:00:00", "shift_type": "STAFFING" },
            { "day": "2026-04-14", "start_time": "09:00:00",
              "end_time": "12:00:00", "shift_type": "MENTORING" }
        ]
    }
    """
    return event_service.create_event(db, data)


@router.put(
    "/admin/events/{event_id}",
    summary="Modifier un événement"
)
def update_event(
    event_id: int,
    data: EventUpdate,   # ✅ NOUVELLE APPROCHE — shifts inclus dans EventUpdate
    db=Depends(get_db),
    super_admin=Depends(get_super_admin)
):
    """
    ✅ NOUVELLE APPROCHE — même body que le CREATE
    Modifie un événement. Seuls les champs envoyés sont modifiés.
    Si shifts fourni → supprime les anciens et recrée les nouveaux.
    Si shifts absent → les créneaux existants ne changent pas.

    Body exemple (modifier seulement les infos) :
    {
        "max_nbr_participant": 150
    }

    Body exemple (modifier infos + remplacer tous les shifts) :
    {
        "max_nbr_participant": 150,
        "shifts": [
            { "day": "2026-04-14", "start_time": "09:00:00",
              "end_time": "12:00:00", "shift_type": "STAFFING" }
        ]
    }
    """
    return event_service.update_event(db, event_id, data)   # ✅ plus de new_shifts séparé


@router.delete(
    "/admin/events/{event_id}",
    summary="Supprimer un événement"
)
def delete_event(
    event_id: int,
    db=Depends(get_db),
    super_admin=Depends(get_super_admin)
):
    """
    Supprime l'événement ET tous ses créneaux.
    Action irréversible.
    """
    return event_service.delete_event(db, event_id)