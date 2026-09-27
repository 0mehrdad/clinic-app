from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["message"] == "Women's Clinic API is running"

def test_get_services():
    response = client.get("/services")

    assert response.status_code == 200

    data = response.json()

    assert "services" in data
    assert len(data["services"]) > 0

    first_service = data["services"][0]

    assert "id" in first_service
    assert "name" in first_service
    assert "duration_minutes" in first_service
    assert "price" in first_service

def test_get_availability():
    response = client.get(
        "/availability",
        params={
            "doctor_id": 1,
            "service_id": 1,
            "appointment_date": "2026-09-21",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["doctor_id"] == 1
    assert data["service_id"] == 1
    assert data["date"] == "2026-09-21"
    assert "available_slots" in data
    assert isinstance(data["available_slots"], list)

def test_create_appointment(db_conn):
    response = client.post(
        "/appointments",
        json={
            "patient_id": 1,
            "doctor_id": 1,
            "service_id": 1,
            "start_time": "2026-09-28T10:00:00",
        },
    )
    print(response.status_code)
    print(response.json())
    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "appointment_id" in data

    appointment_id = data["appointment_id"]

    get_response = client.get(
        f"/appointments/{appointment_id}"
    )

    assert get_response.status_code == 200

    appointment = get_response.json()

    assert appointment["id"] == appointment_id
    assert appointment["patient_id"] == 1
    assert appointment["doctor_id"] == 1
    assert appointment["service_id"] == 1
    assert appointment["status"] == "booked"

def test_api_rejects_double_booking(db_conn):
    appointment = {
        "patient_id": 1,
        "doctor_id": 1,
        "service_id": 1,
        "start_time": "2026-09-28T10:00:00",
    }

    # First booking
    first_response = client.post(
        "/appointments",
        json=appointment,
    )

    assert first_response.status_code == 200
    assert first_response.json()["success"] is True

    # Different patient tries to take the same appointment
    appointment["patient_id"] = 2

    second_response = client.post(
        "/appointments",
        json=appointment,
    )

    assert second_response.status_code == 400

    data = second_response.json()

    assert "detail" in data

def test_api_reschedule_and_cancel_appointment(db_conn):
    # 1. Create appointment
    create_response = client.post(
        "/appointments",
        json={
            "patient_id": 1,
            "doctor_id": 1,
            "service_id": 1,
            "start_time": "2026-09-28T09:00:00",
        },
    )

    assert create_response.status_code == 200

    appointment_id = create_response.json()["appointment_id"]

    # 2. Reschedule from 09:00 to 10:00
    reschedule_response = client.patch(
        f"/appointments/{appointment_id}/reschedule",
        json={
            "new_start_time": "2026-09-28T10:00:00"
        },
    )

    assert reschedule_response.status_code == 200
    assert reschedule_response.json()["success"] is True

    # 3. Retrieve appointment and verify new time
    get_response = client.get(
        f"/appointments/{appointment_id}"
    )

    assert get_response.status_code == 200

    appointment = get_response.json()

    assert appointment["start_time"] == "2026-09-28T10:00:00"
    assert appointment["status"] == "booked"

    # 4. Cancel appointment
    cancel_response = client.patch(
        f"/appointments/{appointment_id}/cancel"
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["success"] is True

    # 5. Retrieve it again and verify cancellation
    final_response = client.get(
        f"/appointments/{appointment_id}"
    )

    assert final_response.status_code == 200

    final_appointment = final_response.json()

    assert final_appointment["status"] == "cancelled"