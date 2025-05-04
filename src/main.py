from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db import Base, engine     # your Base and engine from db.py
from src.routes.auth_routes import router as auth_router  # the router you just made

app = FastAPI()

# Auto-create tables on startup
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the auth router at /api/v1/auth
app.include_router(auth_router, prefix="/api/v1/auth")
