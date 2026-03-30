from pydantic import BaseModel
 from typing import Dict

 class SensorCreate(BaseModel):
     user_id: str
     data: Dict
