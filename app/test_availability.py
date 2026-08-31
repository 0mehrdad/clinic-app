from datetime import date

from database import SessionLocal
from clinic_service import get_available_slots


db = SessionLocal()

try:
    appointment_date = date(2026, 8, 31)

    slots = get_available_slots(
        db=db,
        doctor_id=1,
        service_id=1,
        appointment_date=appointment_date,
    )

    print(f"\nAvailable slots for {appointment_date}")
    print("--------------------------------")

    for slot in slots:
        print(slot.strftime("%H:%M"))

finally:
    db.close()