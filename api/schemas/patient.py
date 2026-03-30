from pydantic import BaseModel
from typing import Optional


class PatientUpdate(BaseModel):
    blood_type: Optional[str] = None
    sex: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None


class PatientOut(BaseModel):
    id: str
    user_id: str
    blood_type: Optional[str] = None
    sex: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
