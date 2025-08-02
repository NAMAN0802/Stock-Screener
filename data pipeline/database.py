from sqlalchemy import Column, Integer, String, ForeignKey, Index, create_engine
from sqlalchemy.orm import declarative_base, relationship, backref
from base import Base
from models import Stocks, Ratios, ProfitLoss, Shareholding, Cashflow, BalanceSheet

class Database:
    def __init__(self):
        self.engine = create_engine("postgresql://naman:password@localhost:5432/stock_screener")

    def create_tables(self):
        Base.metadata.create_all(self.engine)
