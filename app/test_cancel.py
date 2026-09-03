from database import get_connection
from clinic_service import cancel_appointment


conn = get_connection()

try:
    result = cancel_appointment(
        conn=conn,
        appointment_id=1,
    )

    print(result)

finally:
    conn.close()