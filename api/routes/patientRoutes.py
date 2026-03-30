from fastapi import APIRouter
from models.patient import Patient
from models.user import User
from schemas.patient import PatientCreate
from bson import ObjectId

router = APIRouter()

@router.post("/patients")
def create_patient(patient : PatientCreate):
    user = User.objects(id = patient.user_id).first()

    if not user:
        print("User doesn't exist")

    new_patient = Patient(
            user = user,
            blood_type = patient.blood_type,
            sex = patient.sex,
            weight = patient.weight,
            height = patient.height
            ).save()

    return{"message":"Patient created"}
