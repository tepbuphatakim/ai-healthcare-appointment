from fastapi import FastAPI

from appointment.api import appointments_controller, authentication_controller, clear_cache_controller, doctor_patient_controller, doctors_controller, patients_controller

app = FastAPI()



app = FastAPI()

app.include_router(
    appointments_controller.router,
    prefix="/appointments",
    tags=["appointments"],
)
app.include_router(
    doctors_controller.router,
    prefix="/doctors",
    tags=["doctors"],
)
app.include_router(
    patients_controller.router,
    prefix="/patients",
    tags=["patients"],
)
app.include_router(
    doctor_patient_controller.router,
    prefix="/doctor-patient",
    tags=["doctor-patient"],
)
app.include_router(
    clear_cache_controller.router,
    prefix="/cache",
    tags=["cache"],
)
app.include_router(
    authentication_controller.router,
    prefix="/auth",
    tags=["auth"],
)
