from fastapi import FastAPI
from app.api.v1.endpoints import user
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Dopply Backend", version="1.0.0")

# Include routers
app.include_router(user.router, prefix="/api/v1", tags=["User"])

# Middleware (e.g., CORS)
@app.on_event("startup")
def startup_event():
    print("Application startup")

@app.on_event("shutdown")
def shutdown_event():
    print("Application shutdown")
