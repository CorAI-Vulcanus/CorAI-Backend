from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import connect_db
from services.ai_inference import load_artifacts

from routes.userRoutes import router as user_routes
from routes.patientRoutes import router as patient_routes
from routes.adminRoutes import router as admin_routes
from wss.wsRoutes import ws_router

app = FastAPI(title="CorAI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connect_db()
load_artifacts()

app.include_router(user_routes)
app.include_router(patient_routes)
app.include_router(admin_routes)
app.include_router(ws_router)


@app.get("/")
def read_root():
    return {"message": "CorAI API is running"}
