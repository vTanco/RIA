from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.database.session import engine, Base
from backend.database import models # Import models to register them with Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router
from backend.api.api_v1.endpoints import auth, analysis

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# Mount static files (Frontend)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
