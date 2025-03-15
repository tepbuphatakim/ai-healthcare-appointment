from appointment.dto import AppointmentCreate
from appointment.repository.appointment import (
    book_appointment_data,
    check_avialable_date,
    get_all_appointments,
    get_appointment_id,
)
from appointment.service.doctor_patient_service import check_patient_doctor_logic
from sqlalchemy.orm import Session


def get_appointment_by_id(appointment_id: int, db: Session):
    return get_appointment_id(appointment_id, db)


def get_all_appointment(db: Session):
    return get_all_appointments(db)


def book_appointment_logic(appointment: AppointmentCreate, db: Session):
    patient_doctor_assoc = check_patient_doctor_logic(
        appointment.doctor_id, appointment.patient_id
    )

    if not patient_doctor_assoc:
        raise Exception("Sorry, the doctor is not for the patient")

    check_available_date_data = check_avialable_date(appointment.appointment_date, db)

    if not check_available_date_data:
        raise Exception("Sorry, the doctor is not for available for that day")

    return book_appointment_data(appointment.doctor_id, appointment.patient_id, appointment.appointment_date, db)
