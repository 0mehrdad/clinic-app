from fastapi import FastAPI, HTTPException, Query
from datetime import date, datetime
from pydantic import BaseModel

from app.database import get_connection
from clinic_service import (
    get_all_services,
    get_doctors_for_service,
    get_doctor_schedule,
    get_available_slots,
    get_appointment,
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
)

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    service_id: int
    start_time: datetime


app = FastAPI(
    title="Women's Clinic API",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Women's Clinic API is running"
    }


@app.get("/services")
def list_services():
    conn = get_connection()

    try:
        services = get_all_services(conn)

        return {
            "services": [dict(service) for service in services]
        }

    finally:
        conn.close()

@app.get("/services/{service_id}/doctors")
def list_doctors_for_service(service_id: int):
    conn = get_connection()

    try:
        doctors = get_doctors_for_service(
            conn=conn,
            service_id=service_id,
        )

        if not doctors:
            raise HTTPException(
                status_code=404,
                detail="No active doctors found for this service.",
            )

        return {
            "service_id": service_id,
            "doctors": [dict(doctor) for doctor in doctors],
        }

    finally:
        conn.close()


@app.get("/doctors/{doctor_id}/schedule")
def doctor_schedule(doctor_id: int):
    conn = get_connection()

    try:
        schedule = get_doctor_schedule(
            conn=conn,
            doctor_id=doctor_id,
        )

        if not schedule:
            raise HTTPException(
                status_code=404,
                detail="No schedule found for this doctor.",
            )

        return {
            "doctor_id": doctor_id,
            "schedule": [dict(shift) for shift in schedule],
        }

    finally:
        conn.close()


@app.get("/availability")
def availability(
    doctor_id: int = Query(..., gt=0),
    service_id: int = Query(..., gt=0),
    appointment_date: date = Query(...),
):
    conn = get_connection()

    try:
        slots = get_available_slots(
            conn=conn,
            doctor_id=doctor_id,
            service_id=service_id,
            appointment_date=appointment_date,
        )

        return {
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

@app.post("/appointments")
def create_appointment(appointment: AppointmentCreate):
    conn = get_connection()

    try:
        result = book_appointment(
            conn=conn,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            service_id=appointment.service_id,
            start_time=appointment.start_time,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result["message"],
            )

        return result

    finally:
        conn.close()

@app.get("/appointments/{appointment_id}")
def appointment_details(appointment_id: int):
    conn = get_connection()

    try:
        appointment = get_appointment(
            conn=conn,
            appointment_id=appointment_id,
        )

        if appointment is None:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found.",
            )

        return dict(appointment)

    finally:
        conn.close()
@app.patch("/appointments/{appointment_id}/cancel")
def cancel_existing_appointment(appointment_id: int):
    conn = get_connection()

    try:
        result = cancel_appointment(
            conn=conn,
            appointment_id=appointment_id,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result["message"],
            )

        return result

    finally:
        conn.close()
class AppointmentReschedule(BaseModel):
    new_start_time: datetime

@app.patch("/appointments/{appointment_id}/reschedule")
def reschedule_existing_appointment(
    appointment_id: int,
    request: AppointmentReschedule,
):
    conn = get_connection()

    try:
        result = reschedule_appointment(
            conn=conn,
            appointment_id=appointment_id,
            new_start_time=request.new_start_time,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result["message"],
            )

        return result

    finally:
        conn.close()