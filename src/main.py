from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db import Base, engine
from src.routes.auth_routes import router as auth_router

app = FastAPI()

@app.on_event("startup")
async def create_tables():
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth_router, prefix="/api/v1/auth")
