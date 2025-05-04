# src/main.py
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext

# bring in your Stakeholder model and get_db() dependency
from src.models.stakeholder import Stakeholder
from src.db import Base, get_db

# bring in your auth router
from src.routes.auth_routes import router as auth_router

# --- Database setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- FastAPI app ---
app = FastAPI()

# create tables on startup
@app.on_event("startup")
def on_startup():
    # 1) Create any missing tables
    Base.metadata.create_all(bind=engine)

    # 2) Auto–insert default admin if not present
    db = SessionLocal()
    try:
        admin = db.query(Stakeholder).filter(Stakeholder.contact_email == "admin@example.com").first()
        if not admin:
            hashed = pwd_context.hash("FM-System-2025!")
            admin = Stakeholder(
                name="Administrator",
                contact_email="admin@example.com",
                hashed_password=hashed
            )
            db.add(admin)
            db.commit()
            print("➡️  Created default admin@example.com user")
    finally:
        db.close()

# CORS (if you need it)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include your auth router under /api/v1/auth
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    dependencies=[Depends(get_db)]
)
