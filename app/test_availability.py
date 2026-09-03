from datetime import date

from database import get_connection
from clinic_service import get_available_slots


conn = get_connection()

try:
    slots = get_available_slots(
        conn=conn,
        doctor_id=1,
        service_id=1,
        appointment_date=date(2026, 9, 3),
    )

    for slot in slots:
        print(slot.strftime("%Y-%m-%d %H:%M"))

finally:
    conn.close()