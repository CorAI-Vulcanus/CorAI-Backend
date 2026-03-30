from fastapi import APIRouter
from models.sensor import Sensor
from models.user import User
from schemas.sensor import SensorCreate

router = APIRouter()

@router.post("/sensor/{user_id}")
def data_ingest(user_id: str, sensor: SensorCreate):
    user = User.objects(id = user_id).first()

    if not user:
        print("User not found")

    ecg = [
            ecg(
                v_mV = r.v_mV
                t_us = r.t_us
                timestamp = r.timestamp
                )
            for r in sensor.ecg
            ]
    
    Sensor(
            user = user,
            fs = sensor.fs,
            n_samples = sensor.n_samples,
            unit = sensor.unit,
            freq_signal_Hz = sensor.freq_signal_Hz,
            ecg = ecg
            ).save()

    return{"message":"Sensor data stored"}
