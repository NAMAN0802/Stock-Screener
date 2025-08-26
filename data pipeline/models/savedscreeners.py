from sqlalchemy.orm import declarative_base,relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from base import Base

class SavedScreeners(Base):
    __tablename__ = "savedscreeners"
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String,nullable=False)
    user_id = Column(Integer,ForeignKey("user.id"),nullable=False)
    criteria = Column(String)

    user=relationship("User",back_populates="saved_screeners")