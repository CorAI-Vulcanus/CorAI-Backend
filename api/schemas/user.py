from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    email: EmailStr
    phone: Optional[str]

class UserOut(BaseModel):
    id: str
    username: str
    name: str
    email: EmailStr
    role: str
