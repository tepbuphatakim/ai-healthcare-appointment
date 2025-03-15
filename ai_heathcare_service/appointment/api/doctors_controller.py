from fastapi import APIRouter, Depends, HTTPException

from appointment.core.db import get_db
from appointment.dto import DoctorCreate
from appointment.service.doctor_service import get_all_doctors, create_doctor_logic
from sqlalchemy.orm import Session

router = APIRouter()

# db: Session = Depends(get_db)

# Retrieve all appointments
@router.get("/")
def get_doctors(db: Session = Depends(get_db)):
    return get_all_doctors(db)


# Retrieve an appointment by ID
# @router.get("/{appointment_id}")
# def get_appointment(appointment_id: int):
#     return get_appointment_by_id(appointment_id)


# Book an appointment
@router.post("/create")
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):

    try:
        new_doctor = create_doctor_logic(doctor, db)

        return {"message": "success", "doctor_id": new_doctor.id}
    except Exception as e:

        print(f"the server is error: {e}")

        raise HTTPException(status_code=500, detail=str(e))
