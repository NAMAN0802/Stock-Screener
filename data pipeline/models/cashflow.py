from base import Base
from sqlalchemy import Column, Integer, String,ForeignKey,Float,Date
from sqlalchemy.orm import relationship

class CashFlow(Base):
    __tablename__ = "cashflow"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    year = Column(Integer)
    cash_from_operating_activities = Column(Float)
    cash_from_investing_activities = Column(Float)
    cash_from_financing_activities = Column(Float)
    net_cash_flow = Column(Float)
    stock = relationship("Stocks", back_populates="cashflow")