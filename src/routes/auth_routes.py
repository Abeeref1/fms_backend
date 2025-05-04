from fastapi import APIRouter, Depends, HTTPException, status, Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.models.stakeholder import Stakeholder
from src.db import get_db
from pydantic import BaseModel

router = APIRouter()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Stakeholder).filter(Stakeholder.contact_email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # In a real app you'd generate a JWT here. For demo, we return a dummy.
    return TokenResponse(access_token=f"token-{user.id}")

