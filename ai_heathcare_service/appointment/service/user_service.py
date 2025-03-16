from sqlalchemy.orm import Session
from appointment.dto import  UserDTO, UserPatientCreate
from appointment.repository.user_repository import create_user_with_patient_model, get_user_by_username_phone_model

def create_user_logic(db: Session, user: UserPatientCreate):
    return create_user_with_patient_model(db, user)

def get_user_username_phone_logic(db: Session, username: str):
    return get_user_by_username_phone_model(db, username)
    