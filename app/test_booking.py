from datetime import datetime

from database import get_connection
from clinic_service import book_appointment


conn = get_connection()

try:
    result = book_appointment(
        conn=conn,
        patient_id=1,
        doctor_id=1,
        service_id=1,
        start_time=datetime(2026, 9, 3, 10, 0),
    )

    print(result)

finally:
    conn.close()