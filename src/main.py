import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext

# Bring in your models & routes
from src.models.stakeholder import Stakeholder
from src.routes.auth_routes import router as auth_router

# --- Database setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Admin default credentials ---
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "FM-System-2025!")

# --- Password hashing context (must match auth_routes) ---
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# --- FastAPI init ---
app = FastAPI(version="0.1.0")

# --- Auto-create tables & default admin on startup ---
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Only add admin if it doesn't already exist
        if not db.query(Stakeholder).filter(Stakeholder.contact_email == ADMIN_EMAIL).first():
            hashed = pwd_context.hash(ADMIN_PASSWORD)
            admin = Stakeholder(
                name="Administrator",
                contact_email=ADMIN_EMAIL,
                hashed_password=hashed
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()

# --- CORS middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DB session dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Mount auth router ---
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    dependencies=[Depends(get_db)],
)

