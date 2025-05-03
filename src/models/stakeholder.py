from sqlalchemy import Column, Integer, String
from src.db import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Stakeholder(Base):
    __tablename__ = "stakeholders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)

    def check_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.hashed_password)

    def set_password(self, plain_password: str):
        self.hashed_password = pwd_context.hash(plain_password)
