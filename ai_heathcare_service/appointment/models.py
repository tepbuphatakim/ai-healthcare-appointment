import datetime
from sqlalchemy import Column, Engine, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship

from appointment.core.db import Base, engine


doctor_patient_association = Table(
    "doctor_patient_association",
    Base.metadata,
    Column("doctor_id", Integer, ForeignKey("doctors.id"), primary_key=True),
    Column("patient_id", Integer, ForeignKey("patients.id"), primary_key=True),
)


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, index=True)

    appointments = relationship("Appointment", back_populates="patient")  # One-to-Many
    doctors = relationship(
        "Doctor", secondary=doctor_patient_association, back_populates="patients"
    )  # Many-to-Many


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, index=True)

    appointments = relationship("Appointment", back_populates="doctor")  # One-to-Many
    patients = relationship(
        "Patient", secondary=doctor_patient_association, back_populates="doctors"
    )  # Many-to-Many
    profile = relationship(
        "DoctorProfile", back_populates="doctor", uselist=False
    )  # One-to-One


# One-to-One: DoctorProfile (Extra details for Doctor)
class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    specialization = Column(String, index=True)
    experience_years = Column(Integer)

    #
    doctor_id = Column(Integer, ForeignKey("doctors.id"), unique=True)  # One-to-One

    #
    doctor = relationship("Doctor", back_populates="profile")

# One-to-Many: Appointment (Belongs to one Patient & one Doctor)
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    # patient_name = Column(String, index=True)
    # doctor_name = Column(String, index=True)
    # Foreign keys
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

    # appointment_date = Column(DateTime, default=datetime.datetime.utcnow)
    appointment_date = Column(DateTime)


Base.metadata.create_all(bind=engine)
