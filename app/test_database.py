from sqlalchemy import text

from database import SessionLocal


db = SessionLocal()

try:
    result = db.execute(
        text("SELECT name, specialty FROM doctors ORDER BY id")
    )

    doctors = result.fetchall()

    for doctor in doctors:
        print(doctor)

finally:
    db.close()