import datetime
from pydantic import BaseModel, Field


# Define request schema
class AppointmentCreate(BaseModel):
    # patient_id: int
    # doctor_id: int
    patient_name: str
    patient_phone: str
    doctor_name: str
    doctor_phone: str
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


class UserPatientCreate(BaseModel):
    username: str
    password: str
    name: str
    phone_number: str


class UserDTO(BaseModel):
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str
