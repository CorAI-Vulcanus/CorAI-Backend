from pydantic import BaseModel
from typing import List
from datetime import datatime

class SensorECG(BaseModel):
    v_mV: int
    t_us: int
    timestamp: datetime

class SensorData(BaseModel):
    fs: int
    n_samples: int
    unit: str
    ferq_signal_Hz: int
    ecg: List[SensorECG]
