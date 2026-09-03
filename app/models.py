from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class ClinicHours(Base):
    __tablename__ = "clinic_hours"

    id = Column(Integer, primary_key=True)
    weekday = Column(Integer, nullable=False)
    open_time = Column(Time, nullable=False)
    close_time = Column(Time, nullable=False)

    __table_args__ = (
        CheckConstraint("weekday >= 0 AND weekday <= 6"),
        CheckConstraint("close_time > open_time"),
    )


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    specialty = Column(String(100))
    active = Column(Boolean, nullable=False, default=True)

    schedules = relationship(
        "DoctorSchedule",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )

    services = relationship(
        "DoctorService",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )

    appointments = relationship(
        "Appointment",
        back_populates="doctor",
    )


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    duration_minutes = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        CheckConstraint("duration_minutes > 0"),
        CheckConstraint("price >= 0"),
    )

    doctors = relationship(
        "DoctorService",
        back_populates="service",
        cascade="all, delete-orphan",
    )

    appointments = relationship(
        "Appointment",
        back_populates="service",
    )


class DoctorService(Base):
    __tablename__ = "doctor_services"

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id", ondelete="CASCADE"),
        primary_key=True,
    )

    service_id = Column(
        Integer,
        ForeignKey("services.id", ondelete="CASCADE"),
        primary_key=True,
    )

    doctor = relationship(
        "Doctor",
        back_populates="services",
    )

    service = relationship(
        "Service",
        back_populates="doctors",
    )


class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id = Column(Integer, primary_key=True)

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
    )

    weekday = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    __table_args__ = (
        CheckConstraint("weekday >= 0 AND weekday <= 6"),
        CheckConstraint("end_time > start_time"),
    )

    doctor = relationship(
        "Doctor",
        back_populates="schedules",
    )


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(30))
    email = Column(String(255))
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    appointments = relationship(
        "Appointment",
        back_populates="patient",
    )


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False,
    )

    service_id = Column(
        Integer,
        ForeignKey("services.id"),
        nullable=False,
    )

    start_time = Column(DateTime, nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="booked",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('booked', 'cancelled', 'completed', 'no_show')"
        ),
    )

    patient = relationship(
        "Patient",
        back_populates="appointments",
    )

    doctor = relationship(
        "Doctor",
        back_populates="appointments",
    )

    service = relationship(
        "Service",
        back_populates="appointments",
    )