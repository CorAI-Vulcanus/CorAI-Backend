from fastapi import APIRouter, Depends
from schemas.user import UserSignIn, UserLogin, UserUpdate
from controllers import userController
from middleware.auth import get_current_user

router = APIRouter(prefix="/user", tags=["Auth", "User"])


@router.post("/sign-in", status_code=201)
def sign_in(data: UserSignIn):
    return userController.sign_in(data)


@router.post("/login")
def login(data: UserLogin):
    return userController.login(data)


@router.get("/logout")
def logout(token: dict = Depends(get_current_user)):
    return userController.logout()


@router.get("/{user_id}")
def get_user(user_id: str, token: dict = Depends(get_current_user)):
    return userController.get_user(user_id, token)


@router.put("/{user_id}")
def update_user(user_id: str, data: UserUpdate, token: dict = Depends(get_current_user)):
    return userController.update_user(user_id, data, token)
