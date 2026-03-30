from fastapi import FastAPI
from database import connect_db

from routes.userRoutes import router as user_routes
from routes.patientRoutes import router as patient_routes

app = FastAPI()
connect_db()

app.include_router(user_routes)
app.include_router(patient_routes)

@app.get("/")
def read_root():
    return{"message":"Hello World"}
