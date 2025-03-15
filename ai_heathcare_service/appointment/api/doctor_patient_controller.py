from fastapi import APIRouter, HTTPException, Depends

from appointment.core.db import get_db
from appointment.dto import PatientDoctorCreate
from appointment.service.doctor_patient_service import create_patient_doctor_logic, get_all_patient_doctor_logic
from sqlalchemy.orm import Session

router = APIRouter()


# Retrieve all appointments
@router.get("/")
def get_patients_doctors():
    return get_all_patient_doctor_logic()


@router.post("/create")
def create_patient_doctor(patient_doctor: PatientDoctorCreate):

    try:
        new_patient_doctor = create_patient_doctor_logic(patient_doctor)

        return {"message": "success", "new_patient_doctor": new_patient_doctor}
    except Exception as e:
        print(f"the server is error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
