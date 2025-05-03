from fastapi import FastAPI
from src.routes.auth_routes import auth_router

app = FastAPI(
    title="Smart FMS Backend",
    version="1.0.0",
    description="Backend API for Smart FMS system"
)

# Include routers
app.include_router(auth_router)

# Root health check
@app.get("/")
def read_root():
    return {"message": "Hello from Smart FMS Backend!"}
