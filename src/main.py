import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ——— Database setup ————————————————————————————————————————————————
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ——— Password hasher ———————————————————————————————————————————————
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ——— FastAPI app init —————————————————————————————————————————————
app = FastAPI()

# ——— CORS (allow all origins) ———————————————————————————————————————
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ——— DB dependency ————————————————————————————————————————————————
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ——— Import your models & routers ——————————————————————————————————————
from src.models.stakeholder import Stakeholder
from src.routes.auth_routes import router as auth_router

# ——— Startup: create tables + default admin ————————————————————————————
@app.on_event("startup")
def on_startup():
    # 1) create all tables
    Base.metadata.create_all(bind=engine)

    # 2) seed the default admin if missing
    db: Session = SessionLocal()
    try:
        existing = db.query(Stakeholder).filter_by(contact_email="admin@example.com").first()
        if not existing:
            admin = Stakeholder(
                name="Administrator",
                contact_email="admin@example.com",
                hashed_password=pwd_context.hash("FM-System-2025!"),
            )
            db.add(admin)
            db.commit()
            print("✅ Default admin created")
    finally:
        db.close()

# ——— Mount your auth router under /api/v1/auth ————————————————————————
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    dependencies=[Depends(get_db)],
)
