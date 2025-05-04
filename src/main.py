import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext
from src.models.stakeholder import Stakeholder
from src.routes.auth_routes import router as auth_router

# --- Database setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- App init ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    # create tables
    Base.metadata.create_all(bind=engine)
    # ensure default admin
    db = SessionLocal()
    try:
        admin = db.query(Stakeholder).filter_by(contact_email="admin@example.com").first()
        if not admin:
            hashed = pwd_context.hash("FM-System-2025!")
            admin = Stakeholder(name="Administrator", contact_email="admin@example.com", hashed_password=hashed)
            db.add(admin)
            db.commit()
    finally:
        db.close()

# mount auth router
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    dependencies=[Depends(get_db)]
)
