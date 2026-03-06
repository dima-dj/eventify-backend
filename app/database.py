# ================================================================
# app/database.py
# ================================================================
# CE FICHIER gère la connexion à MySQL.
#
# CONCEPT IMPORTANT — "Connection Pool" :
# Au lieu d'ouvrir/fermer une connexion à chaque requête HTTP
# (très lent), on garde un "pool" de connexions ouvertes en
# permanence. Chaque requête en emprunte une, puis la rend.
#
# UTILISATION dans les routers :
#   from app.database import get_db
#   @router.get("/...")
#   def my_route(db = Depends(get_db)):
#       cursor = db.cursor(dictionary=True)
#       ...
# ================================================================

import mysql.connector
from mysql.connector import pooling
from app.config import settings  # nos variables .env


# ----------------------------------------------------------------
# Création du pool de connexions
# pool_size=5 → 5 connexions ouvertes en permanence
# ----------------------------------------------------------------
connection_pool = pooling.MySQLConnectionPool(
    pool_name="eventify_pool",
    pool_size=5,
    pool_reset_session=True,    # remet la connexion à zéro après usage
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    database=settings.DB_NAME,
)


def get_db():
    """
    Fonction "générateur" utilisée avec FastAPI Depends().

    COMMENT ÇA MARCHE :
    1. FastAPI appelle get_db() au début de chaque requête
    2. On emprunte une connexion du pool (connection_pool.get_connection())
    3. On la donne au router avec "yield"
    4. Après la requête (succès OU erreur), le code après yield s'exécute
    5. On remet la connexion dans le pool

    Le bloc try/finally garantit que la connexion est TOUJOURS
    rendue au pool, même si une exception se produit.
    """
    connection = None
    try:
        connection = connection_pool.get_connection()
        yield connection          # ← donne la connexion au router
    finally:
        if connection and connection.is_connected():
            connection.close()    # ← remet au pool (ne ferme pas vraiment)


def get_cursor(connection, dictionary=True):
    """
    Helper pour créer un curseur.
    dictionary=True → les résultats sont des dict {"col": val}
    au lieu de tuples (val1, val2) — beaucoup plus lisible

    UTILISATION :
        cursor = get_cursor(db)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()   # → {"id": 1, "first_name": "Ahmed", ...}
    """
    return connection.cursor(dictionary=dictionary)