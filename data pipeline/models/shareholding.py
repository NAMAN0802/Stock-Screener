from base import Base
from sqlalchemy import Column, Integer, String,ForeignKey,Float,Date
from sqlalchemy.orm import relationship

class Shareholding(Base):
    __tablename__ = "shareholding"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    date = Column(Date)
    promoter_holding = Column(Float)
    fii_holding = Column(Float)
    dii_holding = Column(Float)
    government_holding = Column(Float)
    public_holding = Column(Float)
    stock = relationship("Stock", back_populates="shareholding")