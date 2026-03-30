from fastapi import APIRouter
from models.user import User
from schemas.user import UserCreate, UserOut
from bson import ObjectId

router = APIRouter()

@router.post("/users", response_model = UserOut)
def create_user(user: UserCreate):
    if User.objects(username = user.username).first():
        print("Username exists")

    new_user = User(
            username = user.username,
            password = user.password, #se necesita hasheo
            name = user.name,
            email = user.email,
            phone = user.phone
            ).save()

    return {
            "id":str(new_user.id),
            "username": new_user.username,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
            }
