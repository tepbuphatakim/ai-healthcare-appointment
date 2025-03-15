from sqlalchemy.orm import Session
from fastapi import Depends

from appointment.core.db import get_db
from appointment.dto import DoctorCreate
from appointment.models import Doctor

# db: Session = Depends(get_db)


def get_all_doctors_data(db: Session):
    return db.query(Doctor).all()

def create_doctor_data(doctor: DoctorCreate, db: Session):
    new_doctor = Doctor(name=doctor.name,phone=doctor.phone)
    
    db.add(new_doctor)
    db.commit()
    # TODO: research why do we need refresh here
    db.refresh(new_doctor)
    
    return new_doctor