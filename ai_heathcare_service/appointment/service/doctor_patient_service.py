from appointment.dto import PatientDoctorCreate
from appointment.repository.doctor_patient_repository import check_patient_doctor_data, create_patient_doctor_data, get_all_patient_doctor_data

def check_patient_doctor_logic(doctor_id: int, patient_id: int):
    return check_patient_doctor_data(doctor_id, patient_id)

def create_patient_doctor_logic(patient_doctor: PatientDoctorCreate):
    return create_patient_doctor_data(patient_doctor)

def get_all_patient_doctor_logic():
    return get_all_patient_doctor_data()
    