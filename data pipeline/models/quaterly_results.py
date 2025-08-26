from base import Base
from sqlalchemy import Column, Integer,ForeignKey,Float,String
from sqlalchemy.orm import relationship

class QuaterlyResults(Base):
    __tablename__ = "quaterlyresults"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    date = Column(String)
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
    stock = relationship("Stocks",back_populates="quaterlyresults")