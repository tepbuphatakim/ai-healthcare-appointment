from appointment.dto import PatientCreate
from appointment.repository.patient_repository import create_patient_data, get_all_patients_data
from sqlalchemy.orm import Session


def get_all_patients(db: Session):
    return get_all_patients_data(db)

def create_patient_logic(patient: PatientCreate, db: Session):
    return create_patient_data(patient, db)