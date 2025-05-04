import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# — Database URL & engine —
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# — Session factory & Base class —
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# — Dependency for routes —
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
