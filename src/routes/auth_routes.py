# fms_backend/src/routes/auth_routes.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.db import get_db       # your DB setup helper
from src.models.stakeholder import Stakeholder  # your User model
import bcrypt
import jwt  # if you use JWT tokens, otherwise remove

router = APIRouter()

@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    # read the JSON body
    body = await request.json()
    email = body.get("email")
    password = body.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    user = db.query(Stakeholder).filter(Stakeholder.contact_email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # check password
    if not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # return something—e.g. a token or success message
    token = jwt.encode({"user_id": user.id}, "YOUR_SECRET_KEY", algorithm="HS256")
    return {"access_token": token}
