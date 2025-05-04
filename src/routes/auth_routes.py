from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext

from src.db import get_db
from src.models.stakeholder import Stakeholder

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

# request payload
class LoginRequest(BaseModel):
    email: str
    password: str

# what we send back
class UserInfo(BaseModel):
    id: int
    name: str
    email: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Stakeholder).filter_by(contact_email=data.email).first()
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {
        "access_token": f"token-{user.id}",
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.contact_email,
        },
    }

