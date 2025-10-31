from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from routes.userRoutes import router as userRouter
from routes.dataRoutes import router as dataRouter
from routes.deviceRoutes import router as deviceRouter
from routes.internalRoutes import router as internalRouter

app = FastAPI(title="CorAI Backend", version="0.1.0")

@app.get("/health")
def health(): return {"ok": True}

# REST Endpoints
app.include_router(userRouter)
app.include_router(dataRouter)
app.include_router(deviceRouter)
app.include_router(internalRouter)

