from sqlalchemy import Engine, insert, select
from fastapi import Depends
from sqlalchemy.orm import Session
from appointment.dto import PatientDoctorCreate
from appointment.models import doctor_patient_association

from appointment.core.db import get_db, engine

# db: Session = Depends(get_db)


def check_patient_doctor_data(doctor_id: int, patient_id: int):
    with Session(engine) as session:
        stmt = select(doctor_patient_association).where(
            doctor_patient_association.c.doctor_id == doctor_id,
            doctor_patient_association.c.patient_id == patient_id,
        )

        return session.execute(stmt).fetchone()  # Fetch one record


def create_patient_doctor_data(patientDoctor: PatientDoctorCreate):
    with Session(engine) as session:
        stmt = (
            insert(doctor_patient_association)
            .values(
                doctor_id=patientDoctor.doctor_id, patient_id=patientDoctor.patient_id
            )
            .returning(
                doctor_patient_association.c.doctor_id,
                doctor_patient_association.c.patient_id,
            )
        )

        result = session.execute(stmt).fetchone()
        session.commit()

        return {"doctor_id": result.doctor_id, "patient_id": result.patient_id}


def get_all_patient_doctor_data():
    with Session(engine) as session:
        stmt = select(doctor_patient_association)
        result = session.execute(stmt).fetchall()  # Fetch all records

        # Convert result into a list of dictionaries
        return [
            {"doctor_id": row.doctor_id, "patient_id": row.patient_id} for row in result
        ]
