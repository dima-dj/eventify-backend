# ================================================================
# app/utils/helpers.py
# ================================================================
# Fonctions utilitaires réutilisables dans toute l'application.
# Pas d'accès DB ici — fonctions pures uniquement.
# ================================================================

import random
import string
import secrets
from datetime import datetime, timedelta, timezone


def generate_otp(length: int = 6) -> str:
    """
    Génère un code OTP numérique.
    Exemple : '482931'

    Utilisé dans registrations/service.py après soumission du formulaire.
    """
    return "".join(random.choices(string.digits, k=length))


def otp_expiry(minutes: int = 15) -> datetime:
    """
    Retourne la date d'expiration de l'OTP.
    Par défaut : maintenant + 15 minutes.

    Stocké dans USERS.OTP_EXPIRES_AT en DB.
    """
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def generate_presence_token() -> str:
    """
    Génère un token unique sécurisé pour les liens email.
    Utilisé pour les liens 'Confirmer présence' et 'Annuler participation'.

    Exemple : 'a3f9b2c1d4e5f6a7b8c9d0e1f2a3b4c5'
    Stocké dans REGISTRATION.PRESENCE_TOKEN en DB.
    """
    return secrets.token_hex(32)