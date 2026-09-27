from app.database import get_connection
from app.clinic_service import create_patient

conn = get_connection()

patient = create_patient(
    conn,
    name="Emma Smith",
    phone="07333333333",
    email="emma@example.com",
)

print("NEW PATIENT:", patient)

conn.close()