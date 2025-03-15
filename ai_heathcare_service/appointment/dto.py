import datetime
from pydantic import BaseModel, Field


# Define request schema
class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
        + datetime.timedelta(hours=7)
    )


class DoctorCreate(BaseModel):
    name: str
    phone: str


class PatientCreate(BaseModel):
    name: str
    phone: str


class PatientDoctorCreate(BaseModel):
    doctor_id: int
    patient_id: int
