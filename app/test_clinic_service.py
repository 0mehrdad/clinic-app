from database import SessionLocal
from clinic_service import (
    get_all_services,
    get_doctors_for_service,
    get_doctor_schedule,
)


db = SessionLocal()

try:
    print("\nSERVICES")
    print("----------------")

    services = get_all_services(db)

    for service in services:
        print(
            service["id"],
            service["name"],
            service["duration_minutes"],
            service["price"],
        )


    print("\nDOCTORS FOR SERVICE 1")
    print("----------------")

    doctors = get_doctors_for_service(db, 1)

    for doctor in doctors:
        print(
            doctor["id"],
            doctor["name"],
            doctor["specialty"],
        )


    print("\nSCHEDULE FOR DOCTOR 1")
    print("----------------")

    schedule = get_doctor_schedule(db, 1)

    for shift in schedule:
        print(
            shift["weekday"],
            shift["start_time"],
            shift["end_time"],
        )

finally:
    db.close()