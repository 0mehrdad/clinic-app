import os

os.environ["DATABASE_URL"] = (
    "postgresql://clinic_user:clinic_password@localhost:5432/clinic_test_db"
)

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor


TEST_DATABASE_URL = os.environ["DATABASE_URL"]

@pytest.fixture
def db_conn():
    conn = psycopg2.connect(
        TEST_DATABASE_URL,
        cursor_factory=RealDictCursor,
    )

    yield conn

    conn.rollback()

    with conn.cursor() as cursor:
        cursor.execute("""
            DELETE FROM appointments;
        """)

    conn.commit()
    conn.close()