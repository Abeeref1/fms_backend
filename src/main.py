import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.db import Base, engine, SessionLocal
from src.models.stakeholder import Stakeholder

app = FastAPI()

@app.on_event("startup")
def startup():
    # 1) Create tables
    Base.metadata.create_all(bind=engine)

    # 2) Auto-seed admin@example.com with password FM-System-2025!
    db: Session = SessionLocal()
    if not db.query(Stakeholder).filter(Stakeholder.contact_email == "admin@example.com").first():
        admin = Stakeholder(
            name="Admin",
            contact_email="admin@example.com",
            hashed_password=Stakeholder.get_password_hash("FM-System-2025!")
        )
        db.add(admin)
        db.commit()
    db.close()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount auth routes
from src.routes.auth_routes import router as auth_router
app.include_router(auth_router, prefix="/api/v1/auth")
