from sqlalchemy import text
from datetime import datetime, timedelta

def get_all_services(db):
    query = text("""
        SELECT
            id,
            name,
            description,
            duration_minutes,
            price
        FROM services
        WHERE active = TRUE
        ORDER BY name
    """)

    result = db.execute(query)

    return result.mappings().all()


def get_doctors_for_service(db, service_id: int):
    query = text("""
        SELECT
            d.id,
            d.name,
            d.specialty
        FROM doctors d
        JOIN doctor_services ds
            ON d.id = ds.doctor_id
        WHERE ds.service_id = :service_id
          AND d.active = TRUE
        ORDER BY d.name
    """)

    result = db.execute(
        query,
        {"service_id": service_id}
    )

    return result.mappings().all()


def get_doctor_schedule(db, doctor_id: int):
    query = text("""
        SELECT
            weekday,
            start_time,
            end_time
        FROM doctor_schedules
        WHERE doctor_id = :doctor_id
        ORDER BY weekday, start_time
    """)

    result = db.execute(
        query,
        {"doctor_id": doctor_id}
    )

    return result.mappings().all()

def get_available_slots(
    db,
    doctor_id: int,
    service_id: int,
    appointment_date,
):
    # Get the service and make sure this doctor provides it
    slot_interval = timedelta(minutes=15)

    service_query = text("""
        SELECT
            s.id,
            s.name,
            s.duration_minutes
        FROM services s
        JOIN doctor_services ds
            ON s.id = ds.service_id
        JOIN doctors d
            ON ds.doctor_id = d.id
        WHERE s.id = :service_id
          AND d.id = :doctor_id
          AND s.active = TRUE
          AND d.active = TRUE
    """)

    service = db.execute(
        service_query,
        {
            "service_id": service_id,
            "doctor_id": doctor_id,
        },
    ).mappings().first()

    if service is None:
        return []


    # Python uses:
    # Monday = 0
    # Tuesday = 1
    # ...
    # Sunday = 6
    weekday = appointment_date.weekday()
    clinic_hours_query = text("""
        SELECT
            open_time,
            close_time
        FROM clinic_hours
        WHERE weekday = :weekday
    """)

    clinic_hours = db.execute(
        clinic_hours_query,
        {"weekday": weekday},
    ).mappings().first()

    if clinic_hours is None:
        return []

    # Find the doctor's working hours for that weekday
    schedule_query = text("""
        SELECT
            start_time,
            end_time
        FROM doctor_schedules
        WHERE doctor_id = :doctor_id
          AND weekday = :weekday
        ORDER BY start_time
    """)

    schedules = db.execute(
        schedule_query,
        {
            "doctor_id": doctor_id,
            "weekday": weekday,
        },
    ).mappings().all()

    if not schedules:
        return []


    duration = timedelta(
        minutes=service["duration_minutes"]
    )
    
    appointments_query = text("""
    SELECT
        a.start_time,
        s.duration_minutes
    FROM appointments a
    JOIN services s
        ON a.service_id = s.id
    WHERE a.doctor_id = :doctor_id
      AND DATE(a.start_time) = :appointment_date
      AND a.status = 'booked'
    ORDER BY a.start_time
    """)

    appointments = db.execute(
        appointments_query,
        {
            "doctor_id": doctor_id,
            "appointment_date": appointment_date,
        },
    ).mappings().all()
    available_slots = []


    # Generate appointment slots for every shift
    for schedule in schedules:

        current_time = datetime.combine(
            appointment_date,
            schedule["start_time"],
        )

        shift_end = datetime.combine(
            appointment_date,
            schedule["end_time"],
        )
        doctor_start = datetime.combine(
            appointment_date,
            schedule["start_time"],
        )

        doctor_end = datetime.combine(
            appointment_date,
            schedule["end_time"],
        )

        clinic_open = datetime.combine(
            appointment_date,
            clinic_hours["open_time"],
        )

        clinic_close = datetime.combine(
            appointment_date,
            clinic_hours["close_time"],
        )

        current_time = max(doctor_start, clinic_open)
        shift_end = min(doctor_end, clinic_close)
        while current_time + duration <= shift_end:

            proposed_start = current_time
            proposed_end = current_time + duration

            has_conflict = False

            for appointment in appointments:

                existing_start = appointment["start_time"]

                existing_end = existing_start + timedelta(
                    minutes=appointment["duration_minutes"]
                )

                if (
                    proposed_start < existing_end
                    and proposed_end > existing_start
                ):
                    has_conflict = True
                    break

            if not has_conflict:
                available_slots.append(proposed_start)

            current_time += slot_interval


    return available_slots