from pydantic import BaseModel, EmailStr
from typing import Optional


class UserSignIn(BaseModel):
    user_name: str
    password: str
    name: Optional[str] = None
    email: EmailStr
    phone_number: str
    role: str


class UserLogin(BaseModel):
    user_name: str
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class UserOut(BaseModel):
    id: str
    username: str
    name: Optional[str]
    email: str
    role: str
    is_active: bool
