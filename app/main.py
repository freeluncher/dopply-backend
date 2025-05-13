from fastapi import FastAPI
from app.api.v1.endpoints import user
from app.api.v1.endpoints import monitoring
from app.api.v1.endpoints import admin_doctor_validation
from app.api.v1.endpoints import token_verify
from app.api.v1.endpoints import patient_list
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Dopply Backend", version="1.0.0")

# Include routers
app.include_router(user.router, prefix="/api/v1", tags=["User"])
app.include_router(monitoring.router, prefix="/v1", tags=["monitoring"])
app.include_router(admin_doctor_validation.router, prefix="/v1/admin", tags=["admin"])
app.include_router(token_verify.router, prefix="/v1", tags=["auth"])
app.include_router(patient_list.router, prefix="/v1", tags=["patients"])

# Middleware (e.g., CORS)
@app.on_event("startup")
def startup_event():
    print("Application startup")

@app.on_event("shutdown")
def shutdown_event():
    print("Application shutdown")
