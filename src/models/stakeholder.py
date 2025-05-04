from sqlalchemy import Column, Integer, String
from src.db import Base

class Stakeholder(Base):
    __tablename__ = "stakeholders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
