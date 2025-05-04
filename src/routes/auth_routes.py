from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.db import get_db       # database session dependency
from src.models.stakeholder import Stakeholder  # your user model
import bcrypt
import jwt  # JSON web token library (install via pip install "pyjwt[crypto]")

router = APIRouter()

@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    # Parse JSON body
    body = await request.json()
    email = body.get("email")
    password = body.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    # Lookup user by email
    user = db.query(Stakeholder).filter(Stakeholder.contact_email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate token (replace YOUR_SECRET_KEY)
    token = jwt.encode({"user_id": user.id}, "YOUR_SECRET_KEY", algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}
