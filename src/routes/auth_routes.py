from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

auth_router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@auth_router.post("/login")
def login_user(request: LoginRequest):
    if request.username == "admin" and request.password == "admin123":
        return {"access_token": "mocked_token", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid username or password")
