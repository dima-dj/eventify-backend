from app.database import get_cursor


def get_admin_by_email(db, email: str) -> dict | None:
    #Cherche un admin par son email.


    cursor = get_cursor(db)
    cursor.execute(
        # AS PASSWORD_HASH = renomme la colonne dans le résultat
        "SELECT ID_ADMIN, EMAIL, PASSWORD AS PASSWORD_HASH, ROLE_ADMIN FROM ADMIN WHERE EMAIL = %s",
        (email,) 
    )
    return cursor.fetchone()   # dict ou None


def get_all_admins(db) -> list:
    #Retourne tous les admins en DB.

    cursor = get_cursor(db)
    cursor.execute(
        "SELECT ID_ADMIN, EMAIL, ROLE_ADMIN FROM ADMIN ORDER BY ID_ADMIN ASC"
    )
    return cursor.fetchall()   # liste de dicts


def create_admin(db, email: str, password_hash: str, role: str) -> int:
    #Insère un nouvel admin en DB.
    
    cursor = get_cursor(db)
    cursor.execute(
        "INSERT INTO ADMIN (EMAIL, PASSWORD, ROLE_ADMIN) VALUES (%s, %s, %s)",
        (email, password_hash, role)
    )
    db.commit()          #sauvegardé l'INSERT
    return cursor.lastrowid


def delete_admin(db, admin_id: int) -> bool:
    #Supprime un admin par son ID.

    cursor = get_cursor(db)
    cursor.execute("DELETE FROM ADMIN WHERE ID_ADMIN = %s", (admin_id,))
    db.commit()
    return cursor.rowcount > 0