from fastapi import APIRouter, HTTPException, Depends

from appointment.core.db import get_db
from appointment.dto import AppointmentCreate
from appointment.service.appointment_service import book_appointment_logic, get_all_appointment, get_appointment_by_id
from sqlalchemy.orm import Session

router = APIRouter()


# Retrieve all appointments
@router.get("/")
def get_appointments(db: Session = Depends(get_db)):
    return get_all_appointment(db)


# Retrieve an appointment by ID
@router.get("/{appointment_id}")
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    return get_appointment_by_id(appointment_id)


# Book an appointment
@router.post("/book-appointment")
def book_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    # error = ""
    try:
        new_appointment = book_appointment_logic(appointment)

        # ai_response = chat_with_ollama(f"Confirm the appointment for {appointment.patient_name} with {appointment.doctor_name} on {appointment.appointment_date}.")

        return {"message": "sucess", "appointment_id": new_appointment.id}
        # return {"message": ai_response, "appointment_id": new_appointment.id}
    except Exception as e:

        # @See https://chatgpt.com/c/67c872cd-bdf0-8008-b014-9f20e84a6c5c for error handling
        print(f"the server is error: {e}")
        # error = e

        raise HTTPException(status_code=500, detail=str(e))
        # return {"message": str(e), "status" : 500} 

    # return {"message": error}
