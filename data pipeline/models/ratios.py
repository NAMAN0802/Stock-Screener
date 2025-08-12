from base import Base
from sqlalchemy import Column, Integer, String,ForeignKey,Float
from sqlalchemy.orm import relationship

class Ratios(Base):
    __tablename__ = "ratios"
    id = Column(Integer,primary_key=True,autoincrement=True)
    stock_id = Column(Integer,ForeignKey("stocks.id"),nullable=False)
    year = Column(Integer)
    debtor_days = Column(Integer)
    inventory_days = Column(Integer)
    days_payable = Column(Integer)
    cash_conversion_days = Column(Integer)
    working_capital_days = Column(Integer)
    stock = relationship("Stocks",back_populates="ratios")