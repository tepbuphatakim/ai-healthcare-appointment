from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from appointment.core.jwt import get_password_hash, verify_password
from appointment.dto import UserDTO, UserPatientCreate
from appointment.models import Patient, User

def get_user_by_username_phone_model(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user_with_patient_model(db: Session, user: UserPatientCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.flush()
    
    db_patient = Patient(name=user.name, phone=user.phone_number, user_id=db_user.id)
    db.add(db_patient)
    db.commit()
    db.refresh(db_user)
    db.refresh(db_patient)
    return db_user, db_patient
    # db.commit()
    # db.refresh(db_user)
    # return db_user

def verify_user(db: Session, form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username_phone_model(db, form_data.username)
    if not user:
        return False
    if not verify_password(form_data.password, user.hashed_password):
        return False
    return user