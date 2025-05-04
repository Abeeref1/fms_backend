# fms_backend/src/main.py

import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.routes.auth_routes import router  # <-- matches the name in auth_routes.py

# --- Database setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- App setup ---
app = FastAPI()

@app.on_event("startup")
async def create_tables():
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

# --- Mount the auth router ---
app.include_router(
    router,
    prefix="/api/v1/auth",
    dependencies=[Depends(get_db)]
)
