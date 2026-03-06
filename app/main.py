# create the FastAPI app
# add middleware (CORS)
# include routers (features)

# ================================================================
# app/main.py
# ================================================================
# C'est le POINT D'ENTRÉE de toute l'application FastAPI.
# C'est ce fichier que uvicorn lance :
#   uvicorn app.main:app --reload
#
# CE FICHIER fait 3 choses seulement :
# 1. Crée l'application FastAPI
# 2. Configure CORS (autorise le frontend à appeler l'API)
# 3. Enregistre tous les routers (features)
# ================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# ----------------------------------------------------------------
# On importera les routers ici au fur et à mesure qu'on les crée
# Exemple : from app.features.events.router import router as events_router
# Pour l'instant ils sont commentés — on les décommentera sprint par sprint
# ----------------------------------------------------------------
# from app.features.events.router import router as events_router
# from app.features.registrations.router import router as registrations_router
# from app.features.members.router import router as members_router
# from app.features.auth.router import router as auth_router


# ----------------------------------------------------------------
# Création de l'application
# title et description apparaissent dans la doc Swagger automatique
# Accès à la doc : http://localhost:8000/docs
# ----------------------------------------------------------------
app = FastAPI(
    title="Eventify API",
    description="API de gestion des événements du club",
    version="1.0.0",
    # En production, on désactive la doc Swagger
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


# ----------------------------------------------------------------
# Configuration CORS
# CORS = Cross-Origin Resource Sharing
# Sans ça, le navigateur bloque les requêtes du frontend vers l'API
#
# En développement : on autorise tout (localhost:5500 = Live Server VSCode)
# En production : on mettra uniquement le vrai domaine du site
# ----------------------------------------------------------------
origins = [
    settings.FRONTEND_URL,          # http://localhost:5500 en dev
    "http://localhost:3000",         # au cas où on utilise un autre port
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],             # GET, POST, PUT, DELETE, PATCH, OPTIONS
    allow_headers=["*"],             # Authorization, Content-Type, etc.
)


# ----------------------------------------------------------------
# Enregistrement des routers
# prefix="/api" → tous les endpoints commencent par /api/...
# tags → groupe les endpoints dans la doc Swagger
# ----------------------------------------------------------------
# app.include_router(events_router,        prefix="/api", tags=["Events"])
# app.include_router(registrations_router, prefix="/api", tags=["Registrations"])
# app.include_router(members_router,       prefix="/api", tags=["Members"])
# app.include_router(auth_router,          prefix="/api", tags=["Auth"])


# ----------------------------------------------------------------
# Endpoint de santé — pour vérifier que l'API tourne
# Test : GET http://localhost:8000/health
# ----------------------------------------------------------------
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "app": "Eventify API",
        "version": "1.0.0",
        "debug": settings.DEBUG,
    }