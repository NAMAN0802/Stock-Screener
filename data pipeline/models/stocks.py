from base import Base
from sqlalchemy import Column, Integer, String,Float
from sqlalchemy.orm import relationship

class Stocks(Base):
    __tablename__ = "stocks"
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String,nullable=False,unique=True)
    symbol = Column(String,nullable=False,unique=True)
    market_cap = Column(Integer,nullable=False)
    sector = Column(String,nullable=False)
    industry = Column(String)
    sub_industry = Column(String)
    book_value = Column(Integer)
    roce = Column(Float)
    roe = Column(Float)
    dividend_yield = Column(Float)
    pe_ratio = Column(Float)
    debt_to_equity = Column(Float)
    current_ratio = Column(Float)
    eps = Column(Float)
    pb_ratio = Column(Float)
    interest_coverage = Column(Float)
    opm = Column(Float)
    npm = Column(Float)
    ratios=relationship("Ratios",back_populates="stock",uselist=False)
    shareholding=relationship("Shareholding",back_populates="stock",uselist=False)
    profitloss=relationship("ProfitLoss",back_populates="stock",uselist=False)
    cashflow=relationship("Cashflow",back_populates="stock",uselist=False)
    balancesheet=relationship("BalanceSheet",back_populates="stock",uselist=False)
    quaterlyresults=relationship("QuaterlyResults",back_populates="stock",uselist=False)

