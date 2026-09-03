from database import get_connection


conn = get_connection()

try:
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, specialty
            FROM doctors
            ORDER BY id
        """)

        doctors = cursor.fetchall()

        for doctor in doctors:
            print(doctor)

finally:
    conn.close()