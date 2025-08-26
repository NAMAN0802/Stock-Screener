from base import Base
from sqlalchemy import Column, Integer, String,ForeignKey,Float,Date
from sqlalchemy.orm import relationship

class ProfitLoss(Base):
    __tablename__ = "profitloss"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    year = Column(Integer)
    sales = Column(Float)
    expenses = Column(Float)
    revenue = Column(Float)
    operating_profit = Column(Float)
    opm = Column(Float)
    other_income = Column(Float)
    interest = Column(Float)
    depreciation = Column(Float)
    profit_before_tax = Column(Float)
    tax = Column(Float)
    net_profit = Column(Float)
    ebitda = Column(Float)
    eps = Column(Float)
    dividend_yield = Column(Float)
    stock = relationship("Stocks",back_populates="profitloss")