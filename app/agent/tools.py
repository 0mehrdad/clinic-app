from datetime import date, datetime

from app.database import get_connection
from app.clinic_service import (
    get_all_services,
    get_doctors_for_service,
    get_patient_by_identity,
    get_available_slots,
    book_appointment,
    cancel_appointment,
    create_patient, 
    add_patient_identity,
    reschedule_appointment,
)



def get_services_tool():
    conn = get_connection()

    try:
        services = get_all_services(conn)

        return {
            "success": True,
            "services": [dict(service) for service in services],
        }

    finally:
        conn.close()

def get_doctors_tool(service_id: int):
    conn = get_connection()

    try:
        doctors = get_doctors_for_service(
            conn=conn,
            service_id=service_id,
        )

        return {
            "success": True,
            "service_id": service_id,
            "doctors": [dict(doctor) for doctor in doctors],
        }

    finally:
        conn.close()


def check_availability_tool(
    doctor_id: int,
    service_id: int,
    appointment_date: str,
):
    conn = get_connection()

    try:
        parsed_date = date.fromisoformat(appointment_date)

        slots = get_available_slots(
            conn=conn,
            doctor_id=doctor_id,
            service_id=service_id,
            appointment_date=parsed_date,
        )

        return {
            "success": True,
            "doctor_id": doctor_id,
            "service_id": service_id,
            "date": appointment_date,
            "available_slots": [
                slot.isoformat()
                for slot in slots
            ],
        }

    finally:
        conn.close()

def book_appointment_tool(
    patient_id: int,
    doctor_id: int,
    service_id: int,
    start_time: str,
):
    conn = get_connection()

    try:
        parsed_start_time = datetime.fromisoformat(start_time)

        result = book_appointment(
            conn=conn,
            patient_id=patient_id,
            doctor_id=doctor_id,
            service_id=service_id,
            start_time=parsed_start_time,
        )

        return result

    finally:
        conn.close()
def cancel_appointment_tool(
    appointment_id: int,
):
    conn = get_connection()

    try:
        result = cancel_appointment(
            conn=conn,
            appointment_id=appointment_id,
        )

        return result

    finally:
        conn.close()


def reschedule_appointment_tool(
    appointment_id: int,
    new_start_time: str,
):
    conn = get_connection()

    try:
        parsed_start_time = datetime.fromisoformat(
            new_start_time
        )

        result = reschedule_appointment(
            conn=conn,
            appointment_id=appointment_id,
            new_start_time=parsed_start_time,
        )

        return result

    finally:
        conn.close()

def find_patient_tool(
    identity_type: str,
    identity_value: str,
):
    conn = get_connection()

    try:
        patient = get_patient_by_identity(
            conn,
            identity_type,
            identity_value,
        )

        if patient is None:
            return {
                "success": False,
                "message": "Patient not found.",
            }

        return {
            "success": True,
            "patient": dict(patient),
        }

    finally:
        conn.close()

def register_patient_tool(
    name: str,
    phone: str,
    email: str,
    telegram_chat_id: str,
):
    conn = get_connection()

    try:
        patient = create_patient(
            conn,
            name=name,
            phone=phone,
            email=email,
        )

        add_patient_identity(
            conn,
            patient_id=patient["id"],
            identity_type="telegram",
            identity_value=telegram_chat_id,
            verified=True,
        )

        return {
            "success": True,
            "patient": dict(patient),
        }

    finally:
        conn.close()