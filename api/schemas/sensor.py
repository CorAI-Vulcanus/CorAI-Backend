from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SensorECG(BaseModel):
    v_mV: int
    t_us: int
    timestamp: Optional[datetime] = None


class SensorData(BaseModel):
    fs: int
    n_samples: int
    unit: str
    freq_signal_Hz: int
    ecg: List[SensorECG]
