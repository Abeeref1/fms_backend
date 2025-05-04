import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1) Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2) App init
app = FastAPI()

# 3) Auto-create tables on startup
@app.on_event("startup")
async def create_tables():
    Base.metadata.create_all(bind=engine)

# 4) Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5) DB-session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 6) Include the auth router
from src.routes.auth_routes import router as auth_router
app.include_router(auth_router, prefix="/api/v1/auth", dependencies=[Depends(get_db)])
