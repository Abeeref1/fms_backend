import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.context import CryptContext

from src.routes.auth_routes import router as auth_router
from src.models.stakeholder import Stakeholder

# --- Database setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- App init ---
app = FastAPI()

# Auto-create tables and default admin
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if admin exists
        stmt = select(Stakeholder).where(Stakeholder.contact_email == "admin@example.com")
        if not db.execute(stmt).scalar_one_or_none():
            hashed = pwd_context.hash("FM-System-2025!")
            admin = Stakeholder(
                name="Administrator",
                contact_email="admin@example.com",
                hashed_password=hashed
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mount router
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    dependencies=[Depends(get_db)]
)
