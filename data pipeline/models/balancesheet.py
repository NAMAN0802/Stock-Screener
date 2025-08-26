from base import Base
from sqlalchemy import Column, Integer, String,ForeignKey,Float,Date
from sqlalchemy.orm import relationship

class BalanceSheet(Base):
    __tablename__ = "balancesheet"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    year = Column(Integer)
    equity_capital = Column(Float)
    reserves = Column(Float)
    borrowings = Column(Float)
    other_liabilities = Column(Float)
    total_liabilities = Column(Float)
    fixed_assets = Column(Float)
    cwip = Column(Float)
    investments = Column(Float)
    other_assets = Column(Float)
    total_assets = Column(Float)
    stock = relationship("Stocks", back_populates="balancesheet")