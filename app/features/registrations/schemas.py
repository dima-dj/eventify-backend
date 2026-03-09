
from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

class RegistrationForm(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    discord_username: str
    university: str
    field_of_study: str
    role: Literal["PARTICIPANT", "MENTOR", "STAFF"]

    # Participant spécifique
    team: Optional[str] = None
    prog_languages: Optional[str] = None
    motivation: Optional[str] = None
    expectation: Optional[str] = None
    main_skills: Optional[str] = None
    skill_level: Optional[Literal["BEGINNER","INTERMEDIATE","ADVANCED"]] = None

    # Mentor spécifique
    years_of_experience: Optional[int] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    area_of_expertise: Optional[str] = None
    technologies: Optional[str] = None
    mentored_before: Optional[bool] = False

    # Staff spécifique
    preferred_role: Optional[Literal["TECHNICAL_SUPPORT","LOGISTICS","COMMUNICATION","ORGANIZATION"]] = None
    organized_before: Optional[bool] = False

class EmailRequest(BaseModel):
    email: EmailStr


class VerifyRegistration(BaseModel):
    otp: str
    form: RegistrationForm


from pydantic import BaseModel
from typing import Optional
from datetime import date
from enum import Enum


class StateEnum(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING  = "PENDING"


class RoleEnum(str, Enum):
    PARTICIPANT = "PARTICIPANT"
    MENTOR      = "MENTOR"
    STAFF       = "STAFF"


class ExportFormatEnum(str, Enum):
    XLSX = "xlsx"
    CSV  = "csv"


class RegistrationSummary(BaseModel):
    """
    Résumé d'une registration
    Contient les infos de base du user + son statut.
    """
    id_user:           int
    id_event:          int
    first_name:        str
    last_name:         str
    email:             str
    role:              str
    state:             str
    registration_date: date


class RegistrationDetail(BaseModel):
    """
    Détail complet d'une registration 
    Contient TOUTES les infos : USERS + rôle spécifique + statut.
    """
    # Infos de base USERS
    id_user:           int
    first_name:        str
    last_name:         str
    email:             str
    phone_number:      str
    discord_username:  str
    university:        str
    field_of_study:    str
    role:              str

    # Infos registration
    id_event:          int
    state:             str
    registration_date: date

    # Infos spécifiques au rôle — None si pas ce rôle
    role_details:      Optional[dict] = None


class StateUpdate(BaseModel):
    """
    Body pour approuver ou rejeter 
    Gardé pour référence.
    """
    state: StateEnum