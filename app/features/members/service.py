from app.database import get_db_connection

# -----------------------------
# Insert user et role
# -----------------------------
def insert_user(form_data):
    conn = get_db_connection()
    try:
       cursor = conn.cursor()

    # USERS
       cursor.execute("""
        INSERT INTO USERS 
        (FIRST_NAME,LAST_NAME,EMAIL,PHONE_NUMBER,DISCORD_USERNAME,UNIVERSITY,FIELD_OF_STUDY,ROLE)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        form_data.first_name,
        form_data.last_name,
        form_data.email,
        form_data.phone_number,
        form_data.discord_username,
        form_data.university,
        form_data.field_of_study,
        form_data.role
    ))
       user_id = cursor.lastrowid

    # ROLE TABLE
       if form_data.role == "PARTICIPANT":
           cursor.execute("""
            INSERT INTO PARTICIPANT 
            (ID_USER, TEAM, PROG_LANGUAGES, MOTIVATION, EXPECTATION, MAIN_SKILLS, SKILL_LEVEL)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id,
            form_data.team,
            form_data.prog_languages,
            form_data.motivation,
            form_data.expectation,
            form_data.main_skills,
            form_data.skill_level
        ))
       elif form_data.role == "MENTOR":
        cursor.execute("""
            INSERT INTO MENTOR 
            (ID_USER, YEARS_OF_EXPERIENCE, LINKEDIN, PORTFOLIO, AREA_OF_EXPERTISE, TECHNOLOGIES, MENTORED_BEFORE)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id,
            form_data.years_of_experience,
            form_data.linkedin,
            form_data.portfolio,
            form_data.area_of_expertise,
            form_data.technologies,
            form_data.mentored_before
        ))
       elif form_data.role == "STAFF":
        cursor.execute("""
            INSERT INTO STAFF 
            (ID_USER, PREFERRED_ROLE, ORGANIZED_BEFORE)
            VALUES (%s,%s,%s)
        """, (
            user_id,
            form_data.preferred_role,
            form_data.organized_before
        ))

       conn.commit()
    
       return user_id
    finally:
        if conn.is_connected():
            conn.close()
