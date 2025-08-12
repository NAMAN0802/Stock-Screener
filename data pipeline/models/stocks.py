from base import Base
from sqlalchemy import Column, Integer, String,Float
from sqlalchemy.orm import relationship

class Stocks(Base):
    __tablename__ = "stocks"
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String,nullable=False,unique=True)
    symbol = Column(String,nullable=False,unique=True)
    market_cap = Column(Float,nullable=False)
    sector = Column(String,nullable=False)
    industry = Column(String)
    sub_industry = Column(String)
    book_value = Column(Float)

    roce = Column(Float)
    roe = Column(Float)

    dividend_yield = Column(Float)

    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    ps_ratio = Column(Float)

    eps = Column(Float)
    debt_to_equity = Column(Float)
    current_ratio = Column(Float)
    interest_coverage = Column(Float)
    opm = Column(Float)
    npm = Column(Float)

    ttm_pe_ratio = Column(Float) # Added

    sales_growth_yoy = Column(Float) # Added
    profit_growth_yoy = Column(Float) # Added
    operating_cash_flow_yoy = Column(Float) # Added

    ratios=relationship("Ratios",back_populates="stock")
    shareholding=relationship("Shareholding",back_populates="stock")
    profitloss=relationship("ProfitLoss",back_populates="stock")
    cashflow=relationship("Cashflow",back_populates="stock")
    balancesheet=relationship("BalanceSheet",back_populates="stock")
    quaterlyresults=relationship("QuaterlyResults",back_populates="stock")

