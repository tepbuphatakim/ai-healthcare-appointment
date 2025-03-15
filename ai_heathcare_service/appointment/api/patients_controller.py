from fastapi import APIRouter, HTTPException, Depends

from appointment.core.db import get_db
from appointment.dto import PatientCreate
from appointment.service.patient_service import create_patient_logic, get_all_patients
from sqlalchemy.orm import Session

router = APIRouter()


# Retrieve all appointments
@router.get("/")
def get_patients(db: Session = Depends(get_db)):
    return get_all_patients(db)


@router.post("/create")
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):

    try:
        new_patient = create_patient_logic(patient, db)

        return {"message": "sucess", "new_patient": new_patient.id}
    except Exception as e:
        print(f"the server is error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
