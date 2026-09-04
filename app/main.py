from fastapi import FastAPI, HTTPException, Query
from datetime import date

from app.database import get_connection
from app.clinic_service import (
    get_all_services,
    get_doctors_for_service,
    get_doctor_schedule,
    get_available_slots,
)


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