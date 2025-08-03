from base import Base
from sqlalchemy import Column, Integer, String,ForeignKey,Float,Date
from sqlalchemy.orm import relationship

class ProfitLoss(Base):
    __tablename__ = "profitloss"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    year = Column(Integer)
    sales = Column(Integer)
    expenses = Column(Integer)
    revenue = Column(Float)
    operating_profit = Column(Integer)
    opm = Column(Float)
    other_income = Column(Integer)
    interest = Column(Float)
    depreciation = Column(Float)
    profit_before_tax = Column(Integer)
    tax = Column(Float)
    net_profit = Column(Integer)
    ebitda = Column(Float)
    eps = Column(Float)
    dividend_yield = Column(Float)
    stock = relationship("Stocks",back_populates="profitloss")