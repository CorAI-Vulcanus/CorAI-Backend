from pydantic import BaseModel

class PatientCreate(BaseModel):
    user_id:str
    blood_type:str
    sex:str
    weight:float
    height:float
