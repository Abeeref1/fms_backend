from fastapi import APIRouter, HTTPException, Request
from src.models.stakeholder import Stakeholder
from src.db import SessionLocal

router = APIRouter()

@router.post("/auth/login")
async def login(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    db = SessionLocal()
    try:
        user = db.query(Stakeholder).filter(Stakeholder.contact_email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        # TEMPORARY BYPASS for admin@example.com
        if user.contact_email == "admin@example.com":
            return {
                "message": "Login bypassed for admin@example.com",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.contact_email,
                }
            }

        if user.check_password(password):
            return {
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.contact_email,
                }
            }

        raise HTTPException(status_code=401, detail="Invalid credentials")
    finally:
        db.close()
