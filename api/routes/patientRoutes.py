from fastapi import APIRouter, Depends
from schemas.patient import PatientUpdate
from schemas.sensor import SensorData
from controllers import patientController
from middleware.auth import get_current_user

router = APIRouter(tags=["Patient"])


@router.get("/patients")
def get_patients(token: dict = Depends(get_current_user)):
    return patientController.get_patients(token)


@router.post("/patient/ingest/{user_id}")
def ingest_data(user_id: str, data: SensorData, token: dict = Depends(get_current_user)):
    return patientController.ingest_data(user_id, data, token)


@router.get("/patient/{user_id}/sessions")
def get_sessions(user_id: str, token: dict = Depends(get_current_user)):
    return patientController.get_sessions(user_id, token)


@router.get("/patient/{user_id}")
def get_patient(user_id: str, token: dict = Depends(get_current_user)):
    return patientController.get_patient(user_id, token)


@router.put("/patient/{user_id}")
def update_patient(user_id: str, data: PatientUpdate, token: dict = Depends(get_current_user)):
    return patientController.update_patient(user_id, data, token)
