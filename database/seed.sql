-- =====================================================
-- CLINIC OPENING HOURS
-- 0 = Monday ... 6 = Sunday
-- =====================================================

INSERT INTO clinic_hours (weekday, open_time, close_time)
VALUES
    (0, '08:00', '20:00'),
    (1, '08:00', '20:00'),
    (2, '08:00', '20:00'),
    (3, '08:00', '20:00'),
    (4, '08:00', '20:00'),
    (5, '09:00', '15:00');


-- =====================================================
-- DOCTORS
-- =====================================================

INSERT INTO doctors (name, specialty)
VALUES
    ('Dr Sarah Wilson', 'Gynaecology'),
    ('Dr Alison Sins', 'Women''s Health'),
    ('Dr Emily Carter', 'Dermatology');


-- =====================================================
-- SERVICES
-- =====================================================

INSERT INTO services (name, description, duration_minutes, price)
VALUES
    (
        'Gynaecology Consultation',
        'Consultation for gynaecological concerns and women''s health.',
        45,
        90.00
    ),
    (
        'Women''s Health Consultation',
        'General consultation covering women''s health concerns and preventive care.',
        30,
        70.00
    ),
    (
        'Dermatology Consultation',
        'Assessment of skin, hair, or nail concerns.',
        45,
        85.00
    ),
    (
        'Follow-up Consultation',
        'Follow-up appointment after an initial consultation.',
        20,
        40.00
    ),
    (
        'Contraception Consultation',
        'Consultation regarding contraception options and ongoing management.',
        30,
        65.00
    ),
    (
        'Menopause Consultation',
        'Consultation for menopause-related symptoms and treatment options.',
        45,
        95.00
    );


-- =====================================================
-- WHICH DOCTORS PROVIDE WHICH SERVICES
-- =====================================================

INSERT INTO doctor_services (doctor_id, service_id)
VALUES
    -- Dr Sarah Wilson
    (1, 1),
    (1, 4),
    (1, 5),
    (1, 6),

    -- Dr Aisha Rahman
    (2, 2),
    (2, 4),
    (2, 5),
    (2, 6),

    -- Dr Emily Carter
    (3, 3),
    (3, 4);


-- =====================================================
-- DOCTOR WEEKLY SCHEDULES
-- =====================================================

INSERT INTO doctor_schedules
    (doctor_id, weekday, start_time, end_time)
VALUES
    -- Dr Sarah Wilson
    (1, 0, '09:00', '17:00'),
    (1, 1, '09:00', '17:00'),
    (1, 3, '10:00', '18:00'),

    -- Dr Aisha Rahman
    (2, 1, '10:00', '18:00'),
    (2, 2, '09:00', '17:00'),
    (2, 4, '09:00', '15:00'),

    -- Dr Emily Carter
    (3, 0, '12:00', '20:00'),
    (3, 2, '12:00', '20:00'),
    (3, 5, '09:00', '15:00');


-- =====================================================
-- TEST PATIENTS
-- =====================================================

INSERT INTO patients (name, phone, email)
VALUES
    ('Alice Brown', '07111111111', 'alice@example.com'),
    ('Sophie Green', '07222222222', 'sophie@example.com');