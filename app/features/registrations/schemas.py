
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