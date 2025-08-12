from base import Base
from sqlalchemy import Column, Integer,ForeignKey,Float,Date
from sqlalchemy.orm import relationship

class QuaterlyResults(Base):
    __tablename__ = "quaterlyresults"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    date = Column(Date)
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
    stock = relationship("Stocks",back_populates="quaterlyresults")