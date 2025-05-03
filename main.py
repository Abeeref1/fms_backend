from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.auth_routes import router as auth_router

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_router, prefix="/api/v1/auth")
