# ================================================================
# app/config.py
# ================================================================
# CE FICHIER fait une seule chose :
# Lire les variables du fichier .env et les rendre disponibles
# partout dans l'application via : from app.config import settings
# ================================================================

from pydantic_settings import BaseSettings  # Lit automatiquement le .env


class Settings(BaseSettings):
    """
    Chaque attribut ici correspond à une variable dans .env
    Si la variable n'existe pas dans .env → erreur au démarrage
    C'est voulu : mieux vaut crasher au démarrage que en production
    """

    # --- Base de données ---
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    SMTP_USER: str
    SMTP_PASSWORD: str
    # --- JWT ---
    #JWT_SECRET_KEY: str
    #JWT_ALGORITHM: str = "HS256"    # valeur par défaut si absent du .env
    #JWT_EXPIRE_HOURS: int = 8

    # --- Email ---
    #MAIL_USERNAME: str
    #MAIL_PASSWORD: str
    #MAIL_FROM: str
    #MAIL_PORT: int = 587
    #MAIL_SERVER: str
    #MAIL_TLS: bool = True
    #MAIL_SSL: bool = False

    # --- Application ---
    DEBUG: bool = True
    FRONTEND_URL: str = "http://localhost:5500"

    class Config:
        # Indique à pydantic-settings où chercher le fichier .env
        env_file = ".env"
        env_file_encoding = "utf-8"


# ----------------------------------------------------------------
# On crée UNE SEULE instance de Settings pour toute l'application
# Tous les fichiers feront : from app.config import settings
# ----------------------------------------------------------------
settings = Settings()