from appointment.dto import DoctorCreate
from appointment.repository.doctors import create_doctor_data, get_all_doctors_data
from sqlalchemy.orm import Session

def get_all_doctors(db: Session):
    return get_all_doctors_data(db)

def create_doctor_logic(doctor: DoctorCreate, db: Session):
    return create_doctor_data(doctor, db)