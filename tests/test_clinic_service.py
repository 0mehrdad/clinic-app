from datetime import datetime

from app.clinic_service import (
    get_all_services,
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
    get_appointment,
)


def test_get_all_services(db_conn):
    services = get_all_services(db_conn)

    assert len(services) > 0

    first_service = services[0]

    assert "id" in first_service
    assert "name" in first_service
    assert "duration_minutes" in first_service
    assert "price" in first_service
    
def test_book_appointment(db_conn):
    start_time = datetime(2026, 9, 28, 9, 0)

    result = book_appointment(
        conn=db_conn,
        patient_id=1,
        doctor_id=1,
        service_id=1,
        start_time=start_time,
    )

    assert result["success"] is True
    assert "appointment_id" in result
def test_cannot_double_book_doctor(db_conn):
    start_time = datetime(2026, 9, 28, 9, 0)

    # First booking should succeed
    first_booking = book_appointment(
        conn=db_conn,
        patient_id=1,
        doctor_id=1,
        service_id=1,
        start_time=start_time,
    )

    assert first_booking["success"] is True

    # Second booking at the same time should fail
    second_booking = book_appointment(
        conn=db_conn,
        patient_id=2,
        doctor_id=1,
        service_id=1,
        start_time=start_time,
    )

    assert second_booking["success"] is False
    assert "available" in second_booking["message"].lower()
def test_cannot_book_overlapping_appointment(db_conn):
    first_start = datetime(2026, 9, 28, 9, 0)
    overlapping_start = datetime(2026, 9, 28, 9, 15)

    first_booking = book_appointment(
        conn=db_conn,
        patient_id=1,
        doctor_id=1,
        service_id=1,
        start_time=first_start,
    )

    assert first_booking["success"] is True

    second_booking = book_appointment(
        conn=db_conn,
        patient_id=2,
        doctor_id=1,
        service_id=1,
        start_time=overlapping_start,
    )

    assert second_booking["success"] is False
def test_cancelled_appointment_releases_slot(db_conn):
    start_time = datetime(2026, 9, 28, 9, 0)

    # Patient 1 books the appointment
    first_booking = book_appointment(
        conn=db_conn,
        patient_id=1,
        doctor_id=1,
        service_id=1,
        start_time=start_time,
    )

    assert first_booking["success"] is True

    appointment_id = first_booking["appointment_id"]

    # Cancel the appointment
    cancellation = cancel_appointment(
        conn=db_conn,
        appointment_id=appointment_id,
    )

    assert cancellation["success"] is True

    # Patient 2 should now be able to book the same slot
    second_booking = book_appointment(
        conn=db_conn,
        patient_id=2,
        doctor_id=1,
        service_id=1,
        start_time=start_time,
    )

    assert second_booking["success"] is True
def test_reschedule_appointment(db_conn):
    original_time = datetime(2026, 9, 28, 9, 0)
    new_time = datetime(2026, 9, 28, 10, 0)

    # Book the original appointment
    booking = book_appointment(
        conn=db_conn,
        patient_id=1,
        doctor_id=1,
        service_id=1,
        start_time=original_time,
    )

    assert booking["success"] is True

    appointment_id = booking["appointment_id"]

    # Move it to 10:00
    reschedule = reschedule_appointment(
        conn=db_conn,
        appointment_id=appointment_id,
        new_start_time=new_time,
    )

    assert reschedule["success"] is True

    # Another patient should now be able to take 09:00
    old_slot_booking = book_appointment(
        conn=db_conn,
        patient_id=2,
        doctor_id=1,
        service_id=1,
        start_time=original_time,
    )

    assert old_slot_booking["success"] is True

    # But another patient should NOT be able to take 10:00
    new_slot_booking = book_appointment(
        conn=db_conn,
        patient_id=2,
        doctor_id=1,
        service_id=1,
        start_time=new_time,
    )

    assert new_slot_booking["success"] is False
def test_failed_reschedule_keeps_original_appointment(db_conn):
    first_time = datetime(2026, 9, 28, 9, 0)
    occupied_time = datetime(2026, 9, 28, 10, 0)

    # Patient 1 books 09:00
    first_booking = book_appointment(
        conn=db_conn,
        patient_id=1,
        doctor_id=1,
        service_id=1,
        start_time=first_time,
    )

    assert first_booking["success"] is True

    # Patient 2 books 10:00
    second_booking = book_appointment(
        conn=db_conn,
        patient_id=2,
        doctor_id=1,
        service_id=1,
        start_time=occupied_time,
    )

    assert second_booking["success"] is True

    # Patient 1 tries to move into Patient 2's slot
    reschedule = reschedule_appointment(
        conn=db_conn,
        appointment_id=first_booking["appointment_id"],
        new_start_time=occupied_time,
    )

    assert reschedule["success"] is False

    # Check Patient 1's appointment still exists at 09:00
    appointment = get_appointment(
        conn=db_conn,
        appointment_id=first_booking["appointment_id"],
    )

    assert appointment is not None
    assert appointment["start_time"] == first_time
    assert appointment["status"] == "booked"
def test_cannot_book_outside_doctor_schedule(db_conn):
    invalid_time = datetime(2026, 9, 28, 3, 0)

    booking = book_appointment(
        conn=db_conn,
        patient_id=1,
        doctor_id=1,
        service_id=1,
        start_time=invalid_time,
    )

    assert booking["success"] is False
def test_cannot_book_doctor_for_unsupported_service(db_conn):
    booking = book_appointment(
        conn=db_conn,
        patient_id=1,
        doctor_id=1,
        service_id=3,  
        start_time=datetime(2026, 9, 28, 9, 0),
    )

    assert booking["success"] is False