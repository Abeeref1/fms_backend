from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from src.db import get_db
from src.models.stakeholder import Stakeholder

router = APIRouter()

@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    # parse JSON body
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    # fetch user
    user = db.query(Stakeholder).filter(Stakeholder.contact_email == email).first()

    # verify credentials
    if not user or user.hashed_password != password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )

    # return dummy token
    return {"access_token": "token-1", "token_type": "bearer"}
