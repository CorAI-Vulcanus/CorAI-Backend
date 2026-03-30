from fastapi import APIRouter, Depends
from schemas.user import UserSignIn
from controllers import adminController
from middleware.auth import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
def get_users(token: dict = Depends(require_admin)):
    return adminController.get_users(token)


@router.post("/users", status_code=201)
def create_user(data: UserSignIn, token: dict = Depends(require_admin)):
    return adminController.create_user(data, token)


@router.put("/user/{user_id}")
def deactivate_user(user_id: str, token: dict = Depends(require_admin)):
    return adminController.deactivate_user(user_id, token)


@router.get("/user/{user_id}")
def delete_user(user_id: str, token: dict = Depends(require_admin)):
    return adminController.delete_user(user_id, token)
