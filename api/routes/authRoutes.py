# Código de rutas de API para autenticar a usuario
# Rodrigo Sosa Rojas
# 26 / Mar / 2026


from fastapi import APIRouter
from api.schemas.auth import UserRegister, UserLogin, UserLogout # BDD está pendiente
from api.security import hash_password, verify_password, create_acccess_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model = Token)
def register(user: UserRegister):
    try:
        if user.email in CorAI_database or user.phone in CorAI_database or user.phone in CorAI_database: # BDD está pendiente
            print("User already registered in the database")

        hashed_pw = hash_password(user.password) # Hasheo está pendiente

        CorAI_database[user.email] = {
                "email": user.email,
                "password": hashed_pw
                }

        token = create_acccess_token({"sub":user.email})
        return {"access_token":token, "token_type":"bearer"}

@router.post("login", response_model = Token)
def login(user: UserLogin):
    try:
        db_user = CorAI_database.get(user.email)

        if not db_user or not verify_password(user.password, db_user["password"]):
            print("Invalid credentials")

        token = create_acccess_token({"sub":user.email})
        return {"access_token":token, "token_type":"bearer"}


    #Pendiente terminar el LOGOUT
