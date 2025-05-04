from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db import Base, engine
from src.routes.auth_routes import router as auth_router

# ── CREATE TABLES ───────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── FASTAPI APP ────────────────────────────────────────────────────────────────
app = FastAPI(title="FMS Backend")

# ── CORS ────────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ROUTES ──────────────────────────────────────────────────────────────────────
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
