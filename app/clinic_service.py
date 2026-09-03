from datetime import datetime, timedelta


def get_all_services(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
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

        return cursor.fetchall()


def get_doctors_for_service(conn, service_id: int):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                d.id,
                d.name,
                d.specialty
            FROM doctors d
            JOIN doctor_services ds
                ON d.id = ds.doctor_id
            WHERE ds.service_id = %s
              AND d.active = TRUE
            ORDER BY d.name
        """, (service_id,))

        return cursor.fetchall()


def get_doctor_schedule(conn, doctor_id: int):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                weekday,
                start_time,
                end_time
            FROM doctor_schedules
            WHERE doctor_id = %s
            ORDER BY weekday, start_time
        """, (doctor_id,))

        return cursor.fetchall()


def get_available_slots(
    conn,
    doctor_id: int,
    service_id: int,
    appointment_date,
):
    slot_interval = timedelta(minutes=15)

    # Check that the doctor actually provides this active service
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                s.id,
                s.name,
                s.duration_minutes
            FROM services s
            JOIN doctor_services ds
                ON s.id = ds.service_id
            JOIN doctors d
                ON ds.doctor_id = d.id
            WHERE s.id = %s
              AND d.id = %s
              AND s.active = TRUE
              AND d.active = TRUE
        """, (service_id, doctor_id))

        service = cursor.fetchone()

    if service is None:
        return []

    weekday = appointment_date.weekday()

    # Check clinic opening hours
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                open_time,
                close_time
            FROM clinic_hours
            WHERE weekday = %s
        """, (weekday,))

        clinic_hours = cursor.fetchone()

    if clinic_hours is None:
        return []

    # Get doctor shifts for that day
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                start_time,
                end_time
            FROM doctor_schedules
            WHERE doctor_id = %s
              AND weekday = %s
            ORDER BY start_time
        """, (doctor_id, weekday))

        schedules = cursor.fetchall()

    if not schedules:
        return []

    duration = timedelta(
        minutes=service["duration_minutes"]
    )

    # Existing booked appointments for that doctor/date
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                start_time,
                end_time
            FROM appointments
            WHERE doctor_id = %s
              AND DATE(start_time) = %s
              AND status = 'booked'
            ORDER BY start_time
        """, (doctor_id, appointment_date))

        appointments = cursor.fetchall()

    now = datetime.now()
    available_slots = []

    for schedule in schedules:
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
                existing_end = appointment["end_time"]

                if (
                    proposed_start < existing_end
                    and proposed_end > existing_start
                ):
                    has_conflict = True
                    break

            if not has_conflict and proposed_start > now:
                available_slots.append(proposed_start)

            current_time += slot_interval

    return available_slots

def book_appointment(
    conn,
    patient_id: int,
    doctor_id: int,
    service_id: int,
    start_time: datetime,
):
    # Check patient exists
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id
            FROM patients
            WHERE id = %s
        """, (patient_id,))

        patient = cursor.fetchone()

    if patient is None:
        return {
            "success": False,
            "message": "Patient not found."
        }

    # Check requested time is currently available
    available_slots = get_available_slots(
        conn=conn,
        doctor_id=doctor_id,
        service_id=service_id,
        appointment_date=start_time.date(),
    )

    if start_time not in available_slots:
        return {
            "success": False,
            "message": "Requested appointment time is not available."
        }

    # Get service duration
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT duration_minutes
            FROM services
            WHERE id = %s
              AND active = TRUE
        """, (service_id,))

        service = cursor.fetchone()

    if service is None:
        return {
            "success": False,
            "message": "Service not found."
        }

    end_time = start_time + timedelta(
        minutes=service["duration_minutes"]
    )

    # Create appointment
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO appointments (
                    patient_id,
                    doctor_id,
                    service_id,
                    start_time,
                    end_time,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, 'booked')
                RETURNING id
            """, (
                patient_id,
                doctor_id,
                service_id,
                start_time,
                end_time,
            ))

            appointment = cursor.fetchone()

        conn.commit()

        return {
            "success": True,
            "appointment_id": appointment["id"],
            "message": "Appointment booked successfully."
        }

    except Exception:
        conn.rollback()
        raise

def cancel_appointment(conn, appointment_id: int):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    status,
                    start_time
                FROM appointments
                WHERE id = %s
            """, (appointment_id,))

            appointment = cursor.fetchone()

            if appointment is None:
                return {
                    "success": False,
                    "message": "Appointment not found."
                }

            if appointment["status"] == "cancelled":
                return {
                    "success": False,
                    "message": "Appointment is already cancelled."
                }

            if appointment["status"] != "booked":
                return {
                    "success": False,
                    "message": (
                        f"Appointment cannot be cancelled "
                        f"because its status is '{appointment['status']}'."
                    )
                }

            cursor.execute("""
                UPDATE appointments
                SET
                    status = 'cancelled',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, status
            """, (appointment_id,))

            cancelled = cursor.fetchone()

        conn.commit()

        return {
            "success": True,
            "appointment_id": cancelled["id"],
            "message": "Appointment cancelled successfully."
        }

    except Exception:
        conn.rollback()
        raise

def reschedule_appointment(
    conn,
    appointment_id: int,
    new_start_time: datetime,
):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    patient_id,
                    doctor_id,
                    service_id,
                    status
                FROM appointments
                WHERE id = %s
            """, (appointment_id,))

            appointment = cursor.fetchone()

        if appointment is None:
            return {
                "success": False,
                "message": "Appointment not found."
            }

        if appointment["status"] != "booked":
            return {
                "success": False,
                "message": (
                    f"Appointment cannot be rescheduled "
                    f"because its status is '{appointment['status']}'."
                )
            }

        doctor_id = appointment["doctor_id"]
        service_id = appointment["service_id"]

        # Temporarily ignore this appointment while checking availability.
        # Otherwise it would conflict with itself.
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE appointments
                SET status = 'cancelled'
                WHERE id = %s
            """, (appointment_id,))

        available_slots = get_available_slots(
            conn=conn,
            doctor_id=doctor_id,
            service_id=service_id,
            appointment_date=new_start_time.date(),
        )

        if new_start_time not in available_slots:
            conn.rollback()

            return {
                "success": False,
                "message": "Requested new appointment time is not available."
            }

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT duration_minutes
                FROM services
                WHERE id = %s
            """, (service_id,))

            service = cursor.fetchone()

        new_end_time = new_start_time + timedelta(
            minutes=service["duration_minutes"]
        )

        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE appointments
                SET
                    start_time = %s,
                    end_time = %s,
                    status = 'booked',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id
            """, (
                new_start_time,
                new_end_time,
                appointment_id,
            ))

            updated = cursor.fetchone()

        conn.commit()

        return {
            "success": True,
            "appointment_id": updated["id"],
            "message": "Appointment rescheduled successfully."
        }

    except Exception:
        conn.rollback()
        raise