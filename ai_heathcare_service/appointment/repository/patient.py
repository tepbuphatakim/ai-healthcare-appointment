from sqlalchemy.orm import Session
from fastapi import Depends

from appointment.core.db import get_db
from appointment.dto import DoctorCreate, PatientCreate
from appointment.models import Doctor, Patient

# db: Session = Depends(get_db)


def get_all_patients_data(db: Session):
    return db.query(Patient).all()

def create_patient_data(patient: PatientCreate, db: Session):
    new_patient = Patient(name=patient.name,phone=patient.phone)
    
    db.add(new_patient)
    db.commit()
    # TODO: research why do we need refresh here
    db.refresh(new_patient)
    
    return new_patient