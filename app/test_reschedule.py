from datetime import datetime

from database import get_connection
from clinic_service import reschedule_appointment


conn = get_connection()

try:
    result = reschedule_appointment(
        conn=conn,
        appointment_id=2,
        new_start_time=datetime(2026, 9, 3, 11, 30),
    )

    print(result)

finally:
    conn.close()