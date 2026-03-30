from fastapi import HTTPException
from models.user import User
from models.patient import Patient
from models.sensor import Sensor
from schemas.user import UserSignIn
from middleware.auth import hash_password
from bson import ObjectId
from bson.errors import InvalidId


def _validate_id(user_id: str):
    try:
        ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")


def get_users(token: dict) -> list:
    users = User.objects.all()
    return [
        {
            "id": str(u.id),
            "username": u.username,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
        }
        for u in users
    ]


def create_user(data: UserSignIn, token: dict) -> dict:
    if User.objects(username=data.user_name).first():
        raise HTTPException(status_code=409, detail="Data already in use")
    if User.objects(email=data.email).first():
        raise HTTPException(status_code=409, detail="Data already in use")
    if User.objects(phone=data.phone_number).first():
        raise HTTPException(status_code=409, detail="Data already in use")

    if data.role not in ("Doctor", "Patient", "Admin"):
        raise HTTPException(status_code=400, detail="Invalid input or fields")

    User(
        username=data.user_name,
        password=hash_password(data.password),
        name=data.name,
        email=data.email,
        phone=data.phone_number,
        role=data.role,
    ).save()

    return {"message": "User created successfully"}


def deactivate_user(user_id: str, token: dict) -> dict:
    _validate_id(user_id)
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.update(is_active=False)
    return {"message": "User deactivated successfully"}


def delete_user(user_id: str, token: dict) -> dict:
    _validate_id(user_id)
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    Patient.objects(user=user).delete()
    Sensor.objects(user=user).delete()
    user.delete()

    return {"message": "User deleted successfully"}
