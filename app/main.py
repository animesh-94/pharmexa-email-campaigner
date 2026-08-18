from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import api

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Email Campaign Management System API",
    description="Backend API for the Email Campaign Management System.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix="/api", tags=["API"])

@app.get("/healthz", tags=["System"])
def healthz():
    return {"status": "ok"}
