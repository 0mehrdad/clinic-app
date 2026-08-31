CREATE TABLE clinic_hours (
    id SERIAL PRIMARY KEY,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    open_time TIME NOT NULL,
    close_time TIME NOT NULL,
    CHECK (close_time > open_time)
);


CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialty VARCHAR(100),
    active BOOLEAN NOT NULL DEFAULT TRUE
);


CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    active BOOLEAN NOT NULL DEFAULT TRUE
);


CREATE TABLE doctor_services (
    doctor_id INTEGER NOT NULL
        REFERENCES doctors(id)
        ON DELETE CASCADE,

    service_id INTEGER NOT NULL
        REFERENCES services(id)
        ON DELETE CASCADE,

    PRIMARY KEY (doctor_id, service_id)
);


CREATE TABLE doctor_schedules (
    id SERIAL PRIMARY KEY,

    doctor_id INTEGER NOT NULL
        REFERENCES doctors(id)
        ON DELETE CASCADE,

    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),

    start_time TIME NOT NULL,
    end_time TIME NOT NULL,

    CHECK (end_time > start_time)
);


CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(30),
    email VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,

    patient_id INTEGER NOT NULL
        REFERENCES patients(id),

    doctor_id INTEGER NOT NULL
        REFERENCES doctors(id),

    service_id INTEGER NOT NULL
        REFERENCES services(id),

    start_time TIMESTAMP NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'booked'
        CHECK (status IN ('booked', 'cancelled', 'completed', 'no_show')),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);