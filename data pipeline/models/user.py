from sqlalchemy.orm import declarative_base,relationship
from sqlalchemy import Column, Integer, String
from base import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String,nullable=False)
    email = Column(String,nullable=False, unique=True)
    password = Column(String,nullable=False)

    saved_screeners=relationship("SavedScreeners",back_populates="user")