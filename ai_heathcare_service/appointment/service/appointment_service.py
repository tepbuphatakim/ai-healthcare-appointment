from appointment.dto import AppointmentCreate
from appointment.repository.appointment_repository import (
    book_appointment_data,
    check_avialable_date,
    get_all_appointments,
    get_appointment_id,
)
from appointment.repository.doctors_repository import get_doctor_name_phone_data
from appointment.repository.patient_repository import get_patient_name_phone_data
from appointment.service.doctor_patient_service import check_patient_doctor_logic
from sqlalchemy.orm import Session


def get_appointment_by_id(appointment_id: int, db: Session):
    return get_appointment_id(appointment_id, db)


def get_all_appointment(db: Session):
    return get_all_appointments(db)


def book_appointment_logic(appointment: AppointmentCreate, db: Session):
    
    # doctor_name_lower = appointment.doctor_name.lower()
    # patient_name_lower = appointment.pa
    patient_res = get_patient_name_phone_data(appointment.patient_name, appointment.patient_phone, db)
    
    doctor_res = get_doctor_name_phone_data(appointment.doctor_name, appointment.doctor_phone, db)
    # print("hello 1")
    if not doctor_res:
        raise Exception("Sorry, the doctor is not exist")
    
    patient_doctor_assoc = check_patient_doctor_logic(
        doctor_res.id, patient_res.id
    )

    if not patient_doctor_assoc:
        raise Exception("Sorry, the doctor is not for the patient")

    check_available_date_data = check_avialable_date(appointment.appointment_date, db)

    if check_available_date_data:
        raise Exception("Sorry, the doctor is not for available for that day")

    return book_appointment_data(doctor_res.id, patient_res.id, appointment.appointment_date, db)
