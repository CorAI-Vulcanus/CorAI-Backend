from fastapi import HTTPException
from models.user import User
from schemas.user import UserSignIn, UserLogin, UserUpdate
from middleware.auth import hash_password, verify_password, create_access_token
from bson import ObjectId
from bson.errors import InvalidId


def _validate_id(user_id: str):
    try:
        ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")


def sign_in(data: UserSignIn) -> dict:
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

    return {"message": "Signed in successfully"}


def login(data: UserLogin) -> dict:
    user = User.objects(username=data.user_name).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is inactive")

    token = create_access_token(str(user.id), user.role)
    return {"token": token}


def logout() -> dict:
    return {"message": "Logged out successfully"}


def get_user(user_id: str, token: dict) -> dict:
    _validate_id(user_id)
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user.id),
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
    }


def update_user(user_id: str, data: UserUpdate, token: dict) -> dict:
    _validate_id(user_id)
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if token.get("sub") != user_id and token.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Forbidden action")

    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if updates:
        user.update(**updates)

    return {"message": "User updated successfully"}
