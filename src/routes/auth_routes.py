from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.db import get_db
from src.models.stakeholder import Stakeholder

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Stakeholder).filter(Stakeholder.contact_email == data.email).first()
    if not user or not user.verify_password(data.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    # (In prod you'd issue a JWT; here we return a dummy token:)
    token = f"token-{user.id}"
    return {"access_token": token, "token_type": "bearer"}
