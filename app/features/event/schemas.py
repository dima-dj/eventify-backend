from pydantic import BaseModel, model_validator
from typing import Optional, List
from datetime import datetime, date, time
from enum import Enum

class ShiftTypeEnum(str, Enum):
    STAFFING  = "STAFFING"
    MENTORING = "MENTORING"


class ShiftCreate(BaseModel):
    day:        date
    start_time: time
    end_time:   time
    shift_type: ShiftTypeEnum

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time doit être après start_time")
        return self


class ShiftResponse(BaseModel):
    id_shift:   int
    day:        date
    start_time: time
    end_time:   time
    shift_type: str


class EventCreate(BaseModel):
    start_registration:  datetime
    end_registration:    datetime
    max_nbr_participant: int
    max_nbr_mentor:      int
    max_nbr_staff:       int
    shifts: List[ShiftCreate] = []

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_registration <= self.start_registration:
            raise ValueError("end_registration doit être après start_registration")
        return self

    @model_validator(mode="after")
    def validate_max_numbers(self):
        if self.max_nbr_participant <= 0:
            raise ValueError("max_nbr_participant doit être > 0")
        if self.max_nbr_mentor <= 0:
            raise ValueError("max_nbr_mentor doit être > 0")
        if self.max_nbr_staff <= 0:
            raise ValueError("max_nbr_staff doit être > 0")
        return self


class EventUpdate(BaseModel):
    """
    ✅ NOUVELLE APPROCHE — même structure que EventCreate
    Tous les champs sont Optional — on modifie seulement ce qui est envoyé.
    shifts inclus directement ici → un seul body pour tout modifier.
    Si shifts envoyé → les anciens sont supprimés et remplacés par les nouveaux.
    Si shifts absent (None) → les shifts existants ne changent pas.
    """
    start_registration:  Optional[datetime] = None
    end_registration:    Optional[datetime] = None
    max_nbr_participant: Optional[int] = None
    max_nbr_mentor:      Optional[int] = None
    max_nbr_staff:       Optional[int] = None
    shifts:              Optional[List[ShiftCreate]] = None


class EventResponse(BaseModel):
    id_event:            int
    start_registration:  datetime
    end_registration:    datetime
    max_nbr_participant: int
    max_nbr_mentor:      int
    max_nbr_staff:       int
    shifts:              List[ShiftResponse] = []