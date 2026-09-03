from database import get_connection
from clinic_service import (
    get_all_services,
    get_doctors_for_service,
    get_doctor_schedule,
)


conn = get_connection()

try:
    print("\nSERVICES")
    print("----------------")

    for service in get_all_services(conn):
        print(
            service["id"],
            service["name"],
            service["duration_minutes"],
            service["price"],
        )

    print("\nDOCTORS FOR SERVICE 1")
    print("----------------")

    for doctor in get_doctors_for_service(conn, 1):
        print(
            doctor["id"],
            doctor["name"],
            doctor["specialty"],
        )

    print("\nSCHEDULE FOR DOCTOR 1")
    print("----------------")

    for shift in get_doctor_schedule(conn, 1):
        print(
            shift["weekday"],
            shift["start_time"],
            shift["end_time"],
        )

finally:
    conn.close()