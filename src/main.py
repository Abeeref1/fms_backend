import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .routes.auth_routes import auth_router  # adjust path if needed

# --------------------
# Database setup
# --------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")

# SQLite needs this extra flag; other DBs ignore it
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --------------------
# App initialization
# --------------------
app = FastAPI()

# Auto-create tables on startup
@app.on_event("startup")
async def create_tables():
    Base.metadata.create_all(bind=engine)

# Mount CORS so your React frontend can talk freely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------
# Routers
# --------------------
# All your auth routes (login, signup, etc.)
app.include_router(auth_router, prefix="/api/v1/auth", dependencies=[Depends(get_db)])
