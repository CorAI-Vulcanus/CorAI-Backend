from fastapi import APIRouter
from models.sensor import Sensor
from models.user import User
from schemas.sensor import SensorCreate

router = APIRouter()

@router.post("/sensor")
def data_ingest(data: SensorCreate):
    user = user.objects(id = data.user_id).first()

    if not user:
        print("User not found")

    Sensor(
            user = user
            data = data.data
            ).save()

    return{"message":"Sensor data stored"}
