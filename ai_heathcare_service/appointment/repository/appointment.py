import datetime
from fastapi import Depends
from sqlalchemy.orm import Session

from appointment.core.db import get_db
from appointment.models import Appointment

# db: Session = Depends(get_db)


def get_appointment_id(appointment_id: int, db: Session):
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()


def get_all_appointments(db: Session):
    return db.query(Appointment).all()


def check_avialable_date(appointment_date: datetime, db: Session):
    appointments = (
        db.query(Appointment)
        .filter(Appointment.appointment_date == appointment_date)
        .all()
    )
    return appointments  # Returns a list of matching appointments


def book_appointment_data(doctor_id: int, patient_id: int, appointment_date: datetime, db: Session):
    # TODO: CHECK the booking date if already have book => done
    # TODO: 1 check if the patient is match with doctor type => done
    # TODO: Remove the default date, create the date with the request follow request date pattern => done
    new_appointment = Appointment(
        patient_id=patient_id, doctor_id=doctor_id, appointment_date=appointment_date
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment
