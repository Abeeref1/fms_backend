# src/main.py
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

from src.models.stakeholder import Stakeholder
from src.db import Base, get_db
from src.routes.auth_routes import router as auth_router

# ——— Database setup ———
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ——— Password hashing ———
# switch to pbkdf2_sha256 (no native bcrypt needed)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

app = FastAPI()

# On startup: create tables + default admin
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(Stakeholder).filter(
            Stakeholder.contact_email == "admin@example.com"
        ).first()
        if not admin:
            hashed = pwd_context.hash("FM-System-2025!")
            admin = Stakeholder(
                name="Administrator",
                contact_email="admin@example.com",
                hashed_password=hashed
            )
            db.add(admin)
            db.commit()
            print("✅ Default admin@example.com created")
    finally:
        db.close()

# CORS setup (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount auth router
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    dependencies=[Depends(get_db)]
)
